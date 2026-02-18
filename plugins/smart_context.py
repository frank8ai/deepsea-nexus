"""
Smart Context - 第二大脑核心子功能

功能：
1. 对话摘要存储 - 根据规则保留原文+摘要（已压缩）
2. 记忆库注入 - 提取记忆库关键信息注入上下文
3. 上下文压缩规则 - 根据对话轮数压缩
4. 压缩前抢救 - NOW.md 抢救机制

设计理念：
- 和第二大脑一起启动
- 每次对话后 → 存储摘要
- 每次对话前 → 注入上下文
- 压缩前 → 抢救关键信息

集成位置：
- plugins/smart_context.py
- 和 nexus_core、session_manager 一起启动
"""

import re
import json
import asyncio
import os
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

from ..nexus_core import NexusCore
from .session_manager import SessionManagerPlugin
from ..core.plugin_system import NexusPlugin, PluginMetadata
from ..core.event_bus import EventTypes
from ..compat_async import run_coro_sync
from ..brain.graph_api import configure_graph, graph_add_edge, graph_related_with_evidence


# ===================== 配置 =====================

@dataclass
class ContextCompressionConfig:
    """
    上下文压缩配置
    
    规则配置：
    - 什么时候存储摘要
    - 什么时候注入上下文
    - 根据对话轮数压缩
    - 压缩前抢救关键信息
    """
    # 对话轮数规则 - 编程任务优化配置
    full_rounds: int = 8          # 完整保留最近 8 轮 (编程需要更多上下文)
    summary_rounds: int = 20      # 超过 20 轮只保留摘要 (保留关键决策)
    compress_after_rounds: int = 35  # 超过 35 轮压缩 (长任务归档)
    # token 规则（估算值，非模型真实 token）
    full_tokens_max: int = 8000
    summary_tokens_max: int = 3000
    compressed_tokens_max: int = 2000
    trigger_soft_ratio: float = 0.6
    trigger_hard_ratio: float = 0.85
    
    # 摘要存储规则
    store_summary_enabled: bool = True
    summary_min_length: int = 50
    compress_on_store: bool = True
    summary_on_each_turn: bool = True
    summary_template_enabled: bool = True
    summary_template_fields: Tuple[str, ...] = (
        "summary",
        "decisions",
        "next_actions",
        "questions",
        "entities",
        "keywords",
    )
    topic_switch_enabled: bool = True
    topic_switch_min_overlap_ratio: float = 0.2
    topic_switch_keywords_max: int = 8
    
    # 上下文注入规则
    inject_enabled: bool = True
    inject_threshold: float = 0.6
    inject_max_items: int = 3
    inject_topk_only: bool = True
    inject_max_chars_per_item: int = 360
    inject_max_lines_per_item: int = 8
    inject_max_lines_total: int = 40
    inject_debug: bool = False
    inject_debug_max_chars: int = 200
    inject_mode: str = "balanced"  # conservative | balanced | aggressive
    association_enabled: bool = True
    context_starved_min_chars: int = 16
    decision_block_enabled: bool = True
    decision_block_max: int = 3
    topic_block_enabled: bool = True
    topic_block_max: int = 3
    topic_block_min_keywords: int = 2
    graph_inject_enabled: bool = True
    graph_max_items: int = 3
    graph_evidence_max_chars: int = 120
    adaptive_enabled: bool = True
    adaptive_min_threshold: float = 0.35
    adaptive_max_threshold: float = 0.75
    adaptive_step: float = 0.03
    adaptive_window: int = 40

    # 注入统计
    inject_stats_enabled: bool = True
    inject_stats_window: int = 50
    inject_ratio_alert_enabled: bool = True
    inject_ratio_alert_threshold: float = 0.15
    inject_ratio_alert_streak: int = 2
    inject_ratio_auto_tune: bool = True
    inject_ratio_auto_tune_step: float = 0.05
    inject_ratio_auto_tune_max_items: int = 6
    inject_persist_interval_sec: int = 60

    # 注入信号增强与动态门控
    inject_signal_boost_decision: float = 0.12
    inject_signal_boost_topic: float = 0.08
    inject_signal_boost_summary: float = 0.05
    inject_dynamic_enabled: bool = True
    inject_dynamic_max_items: int = 5
    inject_dynamic_low_signal_penalty: int = 1
    inject_dynamic_high_signal_bonus: int = 1
    
    # 抢救规则 (NOW.md)
    rescue_enabled: bool = True       # 启用压缩前抢救
    rescue_gold: bool = True        # 抢救 #GOLD 标记
    rescue_decisions: bool = True     # 抢救关键决策
    rescue_next_actions: bool = True # 抢救下一步行动


@dataclass
class ConversationContext:
    """
    对话上下文
    
    记录每轮对话的上下文状态
    """
    round_num: int
    status: str  # "full", "summary", "compressed"
    content: str
    created_at: str
    summary: str = ""
    compressed: bool = False
    
    def to_dict(self) -> Dict:
        return asdict(self)


# ===================== Smart Context 核心 =====================

class SmartContextPlugin(NexusPlugin):
    """
    Smart Context 插件
    
    第二大脑核心子功能：
    1. 存储对话摘要（根据规则）
    2. 注入记忆库上下文
    3. 根据对话轮数压缩上下文
    """
    
    def __init__(self):
        super().__init__()
        self.metadata = PluginMetadata(
            name="smart_context",
            version="3.1.0",
            description="Smart context - summary storage, memory injection, context compression",
            dependencies=["nexus_core", "session_manager"],
            hot_reloadable=True,
        )
        self.config = ContextCompressionConfig()
        self._nexus_core = None
        self._session_manager = None
        self._context_history: List[ConversationContext] = []
        self._current_round = 0
        self._graph_enabled = False
        self._inject_history: List[Dict[str, Any]] = []
        self._inject_stats: List[Dict[str, Any]] = []
        self._inject_ratio_streak = 0
        self._config_path: Optional[str] = None
        self._pending_config_updates: Dict[str, Any] = {}
        self._last_persist_ts = 0.0
        self._metrics_path: Optional[str] = None
        self._last_keywords: List[str] = []
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化"""
        try:
            from ..core.plugin_system import get_plugin_registry
            registry = get_plugin_registry()
            self._nexus_core = registry.get("nexus_core")
            self._session_manager = registry.get("session_manager")
            
            if not self._nexus_core:
                print("⚠️ SmartContext: nexus_core 未就绪")
            
            # 加载配置
            if config.get("smart_context"):
                smart_cfg = config["smart_context"]
                self.config = ContextCompressionConfig(
                    full_rounds=smart_cfg.get("full_rounds", 8),
                    summary_rounds=smart_cfg.get("summary_rounds", 30),
                    compress_after_rounds=smart_cfg.get("compress_after_rounds", 50),
                    full_tokens_max=smart_cfg.get("full_tokens_max", 8000),
                    summary_tokens_max=smart_cfg.get("summary_tokens_max", 3000),
                    compressed_tokens_max=smart_cfg.get("compressed_tokens_max", 2000),
                    trigger_soft_ratio=smart_cfg.get("trigger_soft_ratio", 0.6),
                    trigger_hard_ratio=smart_cfg.get("trigger_hard_ratio", 0.85),
                    store_summary_enabled=smart_cfg.get("store_summary_enabled", True),
                    summary_on_each_turn=smart_cfg.get("summary_on_each_turn", True),
                    summary_template_enabled=smart_cfg.get("summary_template_enabled", True),
                    summary_template_fields=tuple(
                        smart_cfg.get(
                            "summary_template_fields",
                            [
                                "summary",
                                "decisions",
                                "next_actions",
                                "questions",
                                "entities",
                                "keywords",
                            ],
                        )
                    ),
                    topic_switch_enabled=smart_cfg.get("topic_switch_enabled", True),
                    topic_switch_min_overlap_ratio=smart_cfg.get("topic_switch_min_overlap_ratio", 0.2),
                    topic_switch_keywords_max=smart_cfg.get("topic_switch_keywords_max", 8),
                    inject_enabled=smart_cfg.get("inject_enabled", True),
                    inject_threshold=smart_cfg.get("inject_threshold", 0.6),
                    inject_max_items=smart_cfg.get("inject_max_items", 3),
                    inject_topk_only=smart_cfg.get("inject_topk_only", True),
                    inject_max_chars_per_item=smart_cfg.get("inject_max_chars_per_item", 360),
                    inject_max_lines_per_item=smart_cfg.get("inject_max_lines_per_item", 8),
                    inject_max_lines_total=smart_cfg.get("inject_max_lines_total", 40),
                    inject_debug=smart_cfg.get("inject_debug", False),
                    inject_debug_max_chars=smart_cfg.get("inject_debug_max_chars", 200),
                    inject_mode=smart_cfg.get("inject_mode", "balanced"),
                    association_enabled=smart_cfg.get("association_enabled", True),
                    context_starved_min_chars=smart_cfg.get("context_starved_min_chars", 16),
                    decision_block_enabled=smart_cfg.get("decision_block_enabled", True),
                    decision_block_max=smart_cfg.get("decision_block_max", 3),
                    topic_block_enabled=smart_cfg.get("topic_block_enabled", True),
                    topic_block_max=smart_cfg.get("topic_block_max", 3),
                    topic_block_min_keywords=smart_cfg.get("topic_block_min_keywords", 2),
                    graph_inject_enabled=smart_cfg.get("graph_inject_enabled", True),
                    graph_max_items=smart_cfg.get("graph_max_items", 3),
                    graph_evidence_max_chars=smart_cfg.get("graph_evidence_max_chars", 120),
                    adaptive_enabled=smart_cfg.get("adaptive_enabled", True),
                    adaptive_min_threshold=smart_cfg.get("adaptive_min_threshold", 0.35),
                    adaptive_max_threshold=smart_cfg.get("adaptive_max_threshold", 0.75),
                    adaptive_step=smart_cfg.get("adaptive_step", 0.03),
                    adaptive_window=smart_cfg.get("adaptive_window", 40),
                    inject_stats_enabled=smart_cfg.get("inject_stats_enabled", True),
                    inject_stats_window=smart_cfg.get("inject_stats_window", 50),
                    inject_ratio_alert_enabled=smart_cfg.get("inject_ratio_alert_enabled", True),
                    inject_ratio_alert_threshold=smart_cfg.get("inject_ratio_alert_threshold", 0.15),
                    inject_ratio_alert_streak=smart_cfg.get("inject_ratio_alert_streak", 2),
                    inject_ratio_auto_tune=smart_cfg.get("inject_ratio_auto_tune", True),
                    inject_ratio_auto_tune_step=smart_cfg.get("inject_ratio_auto_tune_step", 0.05),
                    inject_ratio_auto_tune_max_items=smart_cfg.get("inject_ratio_auto_tune_max_items", 6),
                    inject_persist_interval_sec=smart_cfg.get("inject_persist_interval_sec", 60),
                    inject_signal_boost_decision=smart_cfg.get("inject_signal_boost_decision", 0.12),
                    inject_signal_boost_topic=smart_cfg.get("inject_signal_boost_topic", 0.08),
                    inject_signal_boost_summary=smart_cfg.get("inject_signal_boost_summary", 0.05),
                    inject_dynamic_enabled=smart_cfg.get("inject_dynamic_enabled", True),
                    inject_dynamic_max_items=smart_cfg.get("inject_dynamic_max_items", 5),
                    inject_dynamic_low_signal_penalty=smart_cfg.get("inject_dynamic_low_signal_penalty", 1),
                    inject_dynamic_high_signal_bonus=smart_cfg.get("inject_dynamic_high_signal_bonus", 1),
                    rescue_enabled=smart_cfg.get("rescue_enabled", True),
                    rescue_gold=smart_cfg.get("rescue_gold", True),
                    rescue_decisions=smart_cfg.get("rescue_decisions", True),
                    rescue_next_actions=smart_cfg.get("rescue_next_actions", True),
                )
            graph_cfg = config.get("graph", {}) if isinstance(config.get("graph", {}), dict) else {}
            self._graph_enabled = bool(graph_cfg.get("enabled", False))
            if self._graph_enabled:
                configure_graph(
                    enabled=True,
                    base_path=config.get("paths", {}).get("base", "."),
                    db_path=graph_cfg.get("db_path"),
                )
            self._metrics_path = self._resolve_metrics_path(config)
            self._config_path = self._resolve_config_path()
            self._append_metrics(
                {
                    "event": "smart_context_init",
                    "inject_enabled": bool(self.config.inject_enabled),
                    "adaptive_enabled": bool(self.config.adaptive_enabled),
                    "graph_enabled": bool(self._graph_enabled),
                }
            )
            
            print(f"✅ SmartContext 初始化完成 (规则: {self.config.full_rounds}轮完整/{self.config.summary_rounds}轮摘要/{self.config.compress_after_rounds}轮压缩)")
            return True
            
        except Exception as e:
            print(f"❌ SmartContext 初始化失败: {e}")
            return False
    
    async def start(self) -> bool:
        """启动"""
        print("✅ SmartContext 启动")
        return True
    
    async def stop(self) -> bool:
        """停止"""
        print("✅ SmartContext 停止")
        return True
    
    # ===================== 对话轮数管理 =====================
    
    def get_current_round(self, conversation_id: str) -> int:
        """
        获取当前对话轮数
        
        从会话管理器获取当前轮数
        """
        if self._session_manager and conversation_id:
            try:
                session = self._session_manager.get_session(conversation_id)
                if session and getattr(session, "chunk_count", 0) > 0:
                    return int(session.chunk_count)
            except Exception:
                pass
        return self._current_round
    
    def should_compress(self, round_num: int) -> Tuple[bool, str]:
        """
        判断是否应该压缩
        
        Returns:
            (should_compress, reason)
        """
        if round_num <= self.config.full_rounds:
            return False, "full"  # 最近 N 轮完整保留

        if round_num <= self.config.summary_rounds:
            return True, "summary"  # 中间的轮数只保留摘要

        return True, "compress"  # 更早的轮数压缩

    def _estimate_tokens(self, text: str) -> int:
        if not text:
            return 0
        return max(1, int(len(text) / 3))

    def _context_token_usage(self) -> Dict[str, int]:
        usage = {"full": 0, "summary": 0, "compressed": 0}
        for ctx in self._context_history:
            content = ctx.content or ""
            if ctx.status == "summary":
                content = ctx.summary or content
            elif ctx.status == "compressed":
                content = ctx.summary or content
            usage[ctx.status] = usage.get(ctx.status, 0) + self._estimate_tokens(content)
        return usage

    def _decide_status_with_tokens(self, round_num: int, token_estimate: int) -> Tuple[str, str]:
        should_compress, reason = self.should_compress(round_num)
        status = "summary" if should_compress and reason == "summary" else "compress" if should_compress else "full"

        usage = self._context_token_usage()
        budget_total = self.config.full_tokens_max + self.config.summary_tokens_max + self.config.compressed_tokens_max
        current_total = sum(usage.values()) + token_estimate

        if budget_total > 0:
            if current_total >= budget_total * float(self.config.trigger_hard_ratio):
                status = "compress"
                reason = "token_hard"
            elif current_total >= budget_total * float(self.config.trigger_soft_ratio) and round_num > self.config.full_rounds:
                status = "summary"
                reason = "token_soft"

        if status == "full" and usage["full"] + token_estimate > int(self.config.full_tokens_max):
            status = "summary"
            reason = "full_tokens_max"

        if status == "summary" and usage["summary"] + token_estimate > int(self.config.summary_tokens_max):
            status = "compress"
            reason = "summary_tokens_max"

        return status, reason
    
    # ===================== 上下文处理 =====================
    
    def process_round(self, 
                     conversation_id: str,
                     round_num: int,
                     user_message: str,
                     ai_response: str) -> Dict[str, Any]:
        """
        处理单轮对话
        
        根据轮数决定处理方式：
        - 0-8 轮：完整保留
        - 9-30 轮：只保留摘要
        - 30+ 轮：压缩/归档
        
        Args:
            conversation_id: 对话 ID
            round_num: 当前轮数
            user_message: 用户消息
            ai_response: AI 回复
            
        Returns:
            处理结果
        """
        result = {
            "conversation_id": conversation_id,
            "round_num": round_num,
            "status": "unknown",
            "stored": False,
        }

        token_estimate = self._estimate_tokens(f"{user_message}\n{ai_response}")
        status, reason = self._decide_status_with_tokens(round_num, token_estimate)
        usage_snapshot = self._context_token_usage()

        if status == "full":
            # 完整保留
            result["status"] = "full"
            result["content"] = f"{user_message}\n{ai_response}"
            result["compressed"] = False
            
        elif status == "summary":
            # 只保留摘要
            result["status"] = "summary"
            summary = self._extract_summary(ai_response)
            result["summary"] = summary
            result["compressed"] = False
            
        else:  # compress
            # 压缩
            result["status"] = "compressed"
            summary = self._extract_summary(ai_response)
            result["summary"] = summary
            result["compressed"] = True
            rescue_result = self.rescue_before_compress(f"{user_message}\n{ai_response}")
            result["rescue"] = rescue_result
            self._append_metrics(
                {
                    "event": "rescue_result",
                    "saved": bool(rescue_result.get("saved")),
                    "skipped": bool(rescue_result.get("skipped")),
                    "reason": rescue_result.get("reason", ""),
                    "decisions": rescue_result.get("decisions_rescued", 0),
                    "goals": rescue_result.get("goals_rescued", 0),
                    "questions": rescue_result.get("questions_rescued", 0),
                }
            )
            if rescue_result.get("saved"):
                self._append_metrics(
                    {
                        "event": "rescue_saved",
                        "decisions": rescue_result.get("decisions_rescued", 0),
                        "goals": rescue_result.get("goals_rescued", 0),
                        "questions": rescue_result.get("questions_rescued", 0),
                    }
                )
                print(
                    "[SmartContext] RESCUE before compress "
                    f"decisions={rescue_result.get('decisions_rescued', 0)} "
                    f"goals={rescue_result.get('goals_rescued', 0)} "
                    f"questions={rescue_result.get('questions_rescued', 0)}"
                )
        # Always emit context status for observability (full/summary/compressed)
        self._append_metrics(
            {
                "event": "context_status",
                "status": status,
                "reason": reason,
                "token_estimate": int(token_estimate),
                "full_tokens": int(usage_snapshot.get("full", 0)),
                "summary_tokens": int(usage_snapshot.get("summary", 0)),
                "compressed_tokens": int(usage_snapshot.get("compressed", 0)),
            }
        )
        
        blocks: List[str] = []
        if self.config.decision_block_enabled:
            blocks = self._extract_decision_blocks(f"{user_message}\n{ai_response}")

        if self.config.summary_on_each_turn:
            turn_summary = self._build_turn_summary(
                user_message,
                ai_response,
                blocks if self.config.decision_block_enabled else [],
            )
            if turn_summary:
                if self._nexus_core:
                    self._call_nexus(
                        "add_document",
                        content=turn_summary,
                        title=f"对话 {conversation_id} - 轮{round_num} (摘要卡)",
                        tags=f"type:turn_summary,round:{round_num},conversation:{conversation_id}"
                    )
                    result["stored"] = True
                self._append_metrics({"event": "turn_summary", "len": len(turn_summary)})

        if self._detect_topic_switch(user_message):
            topic_summary = self._build_turn_summary(
                user_message,
                ai_response,
                blocks if self.config.decision_block_enabled else [],
            )
            if topic_summary:
                if self._nexus_core:
                    self._call_nexus(
                        "add_document",
                        content=topic_summary,
                        title=f"对话 {conversation_id} - 话题切换 (轮{round_num})",
                        tags=f"type:topic_boundary,round:{round_num},conversation:{conversation_id}"
                    )
                    result["stored"] = True
                self._append_metrics({"event": "topic_switch", "round": round_num})

        # 存储
        if self._nexus_core:
            self._store_context(conversation_id, round_num, result)
            if blocks:
                self._store_decision_blocks(conversation_id, round_num, blocks)
            if self.config.topic_block_enabled:
                topics = self._extract_topics(f"{user_message}\n{ai_response}")
                if topics:
                    self._store_topic_blocks(conversation_id, round_num, topics)
            result["stored"] = True
        
        # 更新历史
        self._current_round = round_num
        self._context_history.append(
            ConversationContext(
                round_num=round_num,
                status=result["status"],
                content=result.get("content", ""),
                created_at=datetime.now().isoformat(),
                summary=result.get("summary", ""),
                compressed=bool(result.get("compressed")),
            )
        )
        
        return result

    def _call_nexus(self, method_name: str, *args, **kwargs):
        if not self._nexus_core:
            return None
        method = getattr(self._nexus_core, method_name, None)
        if not callable(method):
            return None
        try:
            result = method(*args, **kwargs)
            if asyncio.iscoroutine(result):
                return run_coro_sync(result)
            return result
        except Exception as e:
            print(f"⚠️ SmartContext: 调用 nexus_core.{method_name} 失败: {e}")
            return None

    def _resolve_metrics_path(self, config: Dict[str, Any]) -> str:
        base_path = config.get("paths", {}).get("base", ".")
        base_path = os.path.expanduser(base_path)
        log_dir = os.path.join(base_path, "logs")
        os.makedirs(log_dir, exist_ok=True)
        return os.path.join(log_dir, "smart_context_metrics.log")

    def _resolve_config_path(self) -> str:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        return os.path.join(base_dir, "config.json")

    def _append_metrics(self, payload: Dict[str, Any]) -> None:
        if not self._metrics_path:
            return
        try:
            payload.setdefault("schema_version", "4.3.1")
            payload.setdefault("component", "smart_context")
            payload.setdefault("event", "unknown")
            payload.setdefault("ts", datetime.now().isoformat())
            with open(self._metrics_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
        except Exception:
            return

    def _persist_smart_context_config(self, updates: Dict[str, Any]) -> None:
        if not updates:
            return
        self._pending_config_updates.update(updates)

    def _flush_pending_config_updates(self) -> None:
        if not self._config_path or not self._pending_config_updates:
            return
        now_ts = datetime.now().timestamp()
        interval = max(10, int(self.config.inject_persist_interval_sec))
        if now_ts - self._last_persist_ts < interval:
            return
        try:
            if not os.path.exists(self._config_path):
                return
            with open(self._config_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            smart_cfg = data.get("smart_context", {})
            smart_cfg.update(self._pending_config_updates)
            data["smart_context"] = smart_cfg
            with open(self._config_path, "w", encoding="utf-8") as fh:
                fh.write(json.dumps(data, ensure_ascii=False, indent=2))
            self._pending_config_updates = {}
            self._last_persist_ts = now_ts
        except Exception:
            return
    
    def _extract_summary(self, response: str) -> str:
        """
        提取摘要
        
        优先级：
        1. JSON 格式
        2. ## 📋 总结 格式
        3. 默认摘要
        """
        # JSON 格式
        json_match = re.search(r'```json\s*\n([\s\S]*?)\n```', response)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                return data.get("本次核心产出", data.get("核心产出", ""))
            except json.JSONDecodeError:
                pass
        
        # ## 📋 总结 格式
        summary_match = re.search(r'## 📋 总结[^\n]*\n([\s\S]*?)(?=\n\n|$)', response)
        if summary_match:
            return self._sanitize_summary(summary_match.group(1).strip(), response)
        
        # 默认摘要
        return self._sanitize_summary(response[:200].strip(), response)

    def _sanitize_summary(self, summary: str, fallback: str) -> str:
        summary = (summary or "").strip()
        summary = re.sub(r'```[\s\S]*?```', '', summary).strip()
        if summary.endswith("...") and len(summary) < 10:
            summary = summary[:-3].strip()
        min_len = max(20, int(self.config.summary_min_length / 2))
        entities = self._extract_key_entities(fallback)
        if len(summary) >= min_len:
            summary = self._append_entities(summary, entities)
            self._append_metrics({"event": "summary_ok", "len": len(summary)})
            return summary
        fallback_text = re.sub(r'```[\s\S]*?```', '', (fallback or "")).strip()
        if not fallback_text:
            self._append_metrics({"event": "summary_short", "len": len(summary)})
            return summary
        rebuilt = (fallback_text[:200] + ("..." if len(fallback_text) > 200 else "")).strip()
        rebuilt = self._append_entities(rebuilt, entities)
        self._append_metrics({"event": "summary_fallback", "len": len(rebuilt)})
        return rebuilt

    def _extract_key_entities(self, text: str) -> List[str]:
        if not text:
            return []
        candidates = []
        for match in re.findall(r'([A-Za-z0-9_./\\-]+\\.[A-Za-z0-9]+)', text):
            candidates.append(match)
        for match in re.findall(r'\\b[A-Za-z_][A-Za-z0-9_]{2,}\\(\\)', text):
            candidates.append(match)
        cleaned = []
        for item in candidates:
            if len(item) < 4 or len(item) > 120:
                continue
            lowered = item.lower()
            if lowered.startswith(("sk-", "nvapi-", "ghp_")):
                continue
            if re.search(r'[A-Za-z0-9]{20,}', item):
                continue
            if item not in cleaned:
                cleaned.append(item)
        return cleaned[:5]

    def _append_entities(self, summary: str, entities: List[str]) -> str:
        if not entities:
            return summary
        missing = [e for e in entities if e not in summary]
        if not missing:
            return summary
        suffix = " 关键项: " + ", ".join(missing[:5])
        return (summary + suffix).strip()
    
    def _store_context(self, conversation_id: str, round_num: int, context: Dict):
        """
        存储上下文到向量库
        """
        try:
            if context["status"] == "full":
                # 完整内容
                self._call_nexus(
                    "add_document",
                    content=context["content"],
                    title=f"对话 {conversation_id} - 轮{round_num} (完整)",
                    tags=f"type:full,round:{round_num},conversation:{conversation_id}"
                )
                
            elif context["status"] == "summary":
                # 只存摘要
                self._call_nexus(
                    "add_document",
                    content=f"[摘要] {context['summary']}",
                    title=f"对话 {conversation_id} - 轮{round_num} (摘要)",
                    tags=f"type:summary,round:{round_num},conversation:{conversation_id}"
                )
                
            else:  # compressed
                # 压缩存储
                self._call_nexus(
                    "add_document",
                    content=f"[已压缩] {context['summary']}",
                    title=f"对话 {conversation_id} - 轮{round_num} (已压缩)",
                    tags=f"type:compressed,round:{round_num},conversation:{conversation_id}"
                )
                
        except Exception as e:
            print(f"⚠️ 存储上下文失败: {e}")
    
    # ===================== 功能 1: 摘要存储 =====================
    
    def should_store_summary(self, response: str) -> bool:
        """判断是否应该存储摘要"""
        if not self.config.store_summary_enabled:
            return False
        
        if len(response) < self.config.summary_min_length:
            return False
        
        return True
    
    def extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        words = re.findall(r'\b\w+\b', text.lower())
        
        stop_words = {
            '的', '了', '是', '在', '我', '你', '他', '这', '那',
            '和', '就', '都', '也', '会', '可以', '什么', '怎么',
            '如何', '有没有', '是不是', '能不能'
        }
        
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        return list(dict.fromkeys(keywords))[:5]

    def _is_context_starved(self, user_message: str) -> bool:
        msg = (user_message or "").strip()
        if len(msg) <= self.config.context_starved_min_chars:
            return True
        for kw in ("继续", "接着", "刚才", "上次", "之前", "延续", "帮我继续"):
            if kw in msg:
                return True
        return False

    def _extract_decision_blocks(self, text: str) -> List[str]:
        if not text:
            return []
        blocks: List[str] = []

        json_match = re.search(r'```json\s*\n([\s\S]*?)\n```', text)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                for key in ("本次核心产出", "核心产出", "决策上下文"):
                    val = data.get(key)
                    if isinstance(val, str) and val.strip():
                        blocks.append(val.strip())
            except json.JSONDecodeError:
                pass

        decision_keywords = ("决定", "选择", "采用", "使用", "结论", "方案", "策略", "切换", "改为")
        for raw in text.splitlines():
            line = raw.strip(" \t-•")
            if not line:
                continue
            if "#GOLD" in line:
                line = re.sub(r".*#GOLD[:\\s]*", "", line).strip()
            if any(k in line for k in decision_keywords) and len(line) >= 6:
                blocks.append(line)

        seen = set()
        uniq = []
        for b in blocks:
            if b in seen:
                continue
            seen.add(b)
            uniq.append(b)
        return uniq[: max(1, int(self.config.decision_block_max))]

    def _extract_actions(self, text: str) -> List[str]:
        if not text:
            return []
        actions: List[str] = []
        for raw in text.splitlines():
            line = raw.strip(" \t-•")
            if not line:
                continue
            if line.lower().startswith(("todo", "next", "步骤")):
                actions.append(line)
                continue
            if "下一步" in line or "继续" in line:
                actions.append(line)
        seen = set()
        uniq = []
        for item in actions:
            if item in seen:
                continue
            seen.add(item)
            uniq.append(item)
        return uniq[:5]

    def _extract_questions(self, text: str) -> List[str]:
        if not text:
            return []
        questions: List[str] = []
        for raw in text.splitlines():
            line = raw.strip(" \t-•")
            if not line:
                continue
            if "?" in line or "？" in line:
                questions.append(line)
        seen = set()
        uniq = []
        for item in questions:
            if item in seen:
                continue
            seen.add(item)
            uniq.append(item)
        return uniq[:5]

    def _build_turn_summary(
        self,
        user_message: str,
        ai_response: str,
        decisions: List[str],
    ) -> str:
        summary = self._sanitize_summary(ai_response, ai_response)
        if not self.config.summary_template_enabled:
            return summary
        actions = self._extract_actions(ai_response)
        questions = self._extract_questions(user_message + "\n" + ai_response)
        entities = self._extract_key_entities(user_message + "\n" + ai_response)
        keywords = self.extract_keywords(user_message + " " + ai_response)
        topics = self._extract_topics(user_message + "\n" + ai_response)

        fields = set(self.config.summary_template_fields or ())
        lines: List[str] = []
        if "summary" in fields:
            lines.append(f"Summary: {summary}")
        if "decisions" in fields and decisions:
            lines.append(f"Decisions: {'; '.join(decisions[:3])}")
        if "topics" in fields and topics:
            lines.append(f"Topics: {', '.join(topics[:4])}")
        if "next_actions" in fields and actions:
            lines.append(f"Next: {'; '.join(actions[:3])}")
        if "questions" in fields and questions:
            lines.append(f"Questions: {'; '.join(questions[:3])}")
        if "entities" in fields and entities:
            lines.append(f"Entities: {', '.join(entities[:5])}")
        if "keywords" in fields and keywords:
            lines.append(f"Keywords: {', '.join(keywords[:6])}")

        return "\n".join(lines).strip()

    def _extract_topics(self, text: str) -> List[str]:
        if not text:
            return []
        topics: List[str] = []
        for raw in text.splitlines():
            line = raw.strip(" \t-•")
            if not line:
                continue
            if line.startswith("## "):
                topics.append(line[3:].strip()[:60])
            if any(k in line for k in ("主题", "话题", "模块", "子系统", "项目")) and len(line) <= 80:
                topics.append(line)
        keywords = self.extract_keywords(text)
        if len(keywords) >= int(self.config.topic_block_min_keywords):
            topics.append(" / ".join(keywords[: int(self.config.topic_block_min_keywords) + 1]))
        seen = set()
        uniq = []
        for t in topics:
            t = t.strip()
            if not t or t in seen:
                continue
            seen.add(t)
            uniq.append(t)
        return uniq[: max(1, int(self.config.topic_block_max))]

    def _detect_topic_switch(self, user_message: str) -> bool:
        if not self.config.topic_switch_enabled:
            return False
        msg = (user_message or "").strip()
        if any(k in msg for k in ("换个话题", "另一个问题", "新话题", "顺便问", "另外")):
            return True
        keywords = self.extract_keywords(msg)[: int(self.config.topic_switch_keywords_max)]
        if not keywords:
            return False
        if not self._last_keywords:
            self._last_keywords = keywords
            return False
        overlap = len(set(keywords) & set(self._last_keywords))
        ratio = overlap / float(max(1, len(set(keywords))))
        self._last_keywords = keywords
        return ratio <= float(self.config.topic_switch_min_overlap_ratio)

    def _trim_injected_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not items:
            return []
        max_chars = max(80, int(self.config.inject_max_chars_per_item))
        max_lines_per = max(2, int(self.config.inject_max_lines_per_item))
        max_lines_total = max(10, int(self.config.inject_max_lines_total))

        trimmed: List[Dict[str, Any]] = []
        used_lines = 0
        for item in items:
            content = (item.get("content") or "").strip()
            if not content:
                continue
            lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
            if len(lines) > max_lines_per:
                lines = lines[:max_lines_per]
            text = "\n".join(lines)
            if len(text) > max_chars:
                text = text[:max_chars].rstrip() + "..."
            line_count = max(1, text.count("\n") + 1)
            if used_lines + line_count > max_lines_total:
                break
            used_lines += line_count
            item = dict(item)
            item["content"] = text
            trimmed.append(item)
        return trimmed

    def _normalize_tags(self, metadata: Any) -> List[str]:
        tags: List[str] = []
        if isinstance(metadata, dict):
            raw = metadata.get("tags") or []
            if isinstance(raw, list):
                tags.extend([str(t).strip() for t in raw if str(t).strip()])
            elif isinstance(raw, str):
                tags.extend([t.strip() for t in raw.split(",") if t.strip()])
        return tags

    def _score_injected_item(self, relevance: float, tags: List[str], source: str) -> float:
        score = float(relevance or 0.0)
        tag_str = ",".join(tags)
        if "type:decision_block" in tag_str or "决策块" in (source or ""):
            score += float(self.config.inject_signal_boost_decision)
        if "type:topic_block" in tag_str or "主题块" in (source or ""):
            score += float(self.config.inject_signal_boost_topic)
        if "type:summary" in tag_str or "摘要" in (source or ""):
            score += float(self.config.inject_signal_boost_summary)
        return min(1.5, score)

    def _has_signal_tag(self, tags: List[str], source: str) -> bool:
        if not tags and not source:
            return False
        tag_str = ",".join(tags)
        if "type:decision_block" in tag_str or "type:topic_block" in tag_str:
            return True
        if "决策块" in (source or "") or "主题块" in (source or ""):
            return True
        return False

    def _dynamic_inject_params(self, reason: str, items: List[Dict[str, Any]]) -> Tuple[int, float]:
        max_items = int(self.config.inject_max_items)
        threshold = float(self.config.inject_threshold)

        if reason == "context_starved":
            max_items = max(1, min(2, max_items))
            threshold = max(0.0, min(1.0, threshold * 0.85))

        if not self.config.inject_dynamic_enabled:
            return max_items, threshold

        signal_hits = sum(1 for item in items if self._has_signal_tag(item.get("tags", []), item.get("source", "")))
        if signal_hits == 0:
            max_items = max(1, max_items - int(self.config.inject_dynamic_low_signal_penalty))
            threshold = min(0.95, threshold + 0.05)
        elif signal_hits >= 2:
            max_items = min(int(self.config.inject_dynamic_max_items), max_items + int(self.config.inject_dynamic_high_signal_bonus))
            threshold = max(0.0, threshold - 0.05)

        return max_items, threshold

    def _extract_graph_edges(self, block: str, conversation_id: str) -> List[Dict[str, Any]]:
        if not block:
            return []
        subj = f"conversation:{conversation_id}" if conversation_id else "workspace"
        edges: List[Dict[str, Any]] = []
        patterns = [
            (r"(使用|采用|选择|改为|切换到)\s*([\\w\\-./]+)", "uses"),
            (r"(依赖|基于)\s*([\\w\\-./]+)", "depends_on"),
            (r"(目标|目的)[:：]\\s*([^，。]+)", "goal"),
            (r"(影响|导致)\\s*([^，。]+)", "impacts"),
        ]
        for pattern, rel in patterns:
            match = re.search(pattern, block)
            if match:
                obj = match.group(2).strip()
                if 2 <= len(obj) <= 80:
                    edges.append(
                        {
                            "subj": subj,
                            "rel": rel,
                            "obj": obj,
                            "weight": 1.0,
                            "entity_types": {"subj": "conversation", "obj": "concept"},
                        }
                    )
        return edges[: self.config.decision_block_max]

    def _store_decision_blocks(self, conversation_id: str, round_num: int, blocks: List[str]) -> None:
        if not blocks:
            return
        for idx, block in enumerate(blocks, 1):
            self._call_nexus(
                "add_document",
                content=block,
                title=f"决策块 {conversation_id} - 轮{round_num} ({idx})",
                tags=f"type:decision_block,round:{round_num},conversation:{conversation_id}"
            )
            if self._graph_enabled:
                for edge in self._extract_graph_edges(block, conversation_id):
                    graph_add_edge(
                        subj=edge["subj"],
                        rel=edge["rel"],
                        obj=edge["obj"],
                        weight=edge.get("weight", 1.0),
                        source=f"decision_block:{conversation_id}",
                        evidence_text=block,
                        conversation_id=conversation_id,
                        round_num=round_num,
                        entity_types=edge.get("entity_types"),
                    )

    def _store_topic_blocks(self, conversation_id: str, round_num: int, topics: List[str]) -> None:
        if not topics:
            return
        for idx, topic in enumerate(topics, 1):
            self._call_nexus(
                "add_document",
                content=topic,
                title=f"主题块 {conversation_id} - 轮{round_num} ({idx})",
                tags=f"type:topic_block,round:{round_num},conversation:{conversation_id}"
            )
            if self._graph_enabled:
                graph_add_edge(
                    subj=f"conversation:{conversation_id}",
                    rel="topic",
                    obj=topic[:80],
                    weight=0.8,
                    source=f"topic_block:{conversation_id}",
                    evidence_text=topic,
                    conversation_id=conversation_id,
                    round_num=round_num,
                    entity_types={"subj": "conversation", "obj": "topic"},
                )
    
    def store_conversation(self, 
                          conversation_id: str,
                          user_message: str,
                          ai_response: str) -> Dict[str, Any]:
        """
        存储对话摘要（兼容旧 API）
        """
        result = {
            "conversation_id": conversation_id,
            "stored": False,
        }
        
        if not self.should_store_summary(ai_response):
            return result
        
        if not self._nexus_core:
            return result
        
        try:
            # 存储原文
            self._call_nexus(
                "add_document",
                content=ai_response,
                title=f"对话 {conversation_id} - 原文",
                tags=f"type:content,source:{conversation_id}"
            )
            result["stored"] = True
            
            # 存储摘要
            summary = self._extract_summary(ai_response)
            if summary:
                self._call_nexus(
                    "add_document",
                    content=f"[摘要] {summary}",
                    title=f"对话 {conversation_id} - 摘要",
                    tags=f"type:summary,source:{conversation_id}"
                )
            
            # 存储关键词
            keywords = self.extract_keywords(user_message + " " + ai_response)
            if keywords:
                self._call_nexus(
                    "add_document",
                    content=" ".join(keywords),
                    title=f"对话 {conversation_id} - 关键词",
                    tags=f"type:keywords,source:{conversation_id}"
                )

            if self.config.decision_block_enabled:
                blocks = self._extract_decision_blocks(f"{user_message}\n{ai_response}")
                self._store_decision_blocks(conversation_id, 0, blocks)

            if self.config.topic_block_enabled:
                topics = self._extract_topics(f"{user_message}\n{ai_response}")
                if topics:
                    self._store_topic_blocks(conversation_id, 0, topics)
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    # ===================== 功能 2: 上下文注入 =====================
    
    def should_inject(self, user_message: str) -> Tuple[bool, str]:
        """
        判断是否需要注入上下文
        """
        if not self.config.inject_enabled:
            return False, "disabled"

        if self.config.association_enabled and self._is_context_starved(user_message):
            return True, "context_starved"
        
        question_patterns = [
            r'怎么', r'如何', r'是什么', r'为什么', r'哪些',
            r'区别', r'实现', r'使用', r'解决'
        ]
        
        for pattern in question_patterns:
            if re.search(pattern, user_message):
                return True, "question"
        
        keywords = self.extract_keywords(user_message)
        mode = (self.config.inject_mode or "balanced").strip().lower()
        if mode == "aggressive":
            if any(k for k in keywords if len(k) > 3):
                return True, "keyword"
        elif mode == "conservative":
            if any(k for k in keywords if len(k) > 8):
                return True, "technical_term"
        else:  # balanced
            if any(k for k in keywords if len(k) > 6):
                return True, "technical_term"
        
        return False, "none"
    
    def inject_memory(self, user_message: str) -> List[Dict]:
        """
        注入记忆库上下文
        """
        should_inject, reason = self.should_inject(user_message)
        
        if not should_inject:
            if self.config.inject_debug:
                print(f"[SmartContext] INJECT skip reason={reason}")
            return []
        
        if not self._nexus_core:
            if self.config.inject_debug:
                print("[SmartContext] INJECT skip nexus_core=missing")
            self._append_metrics(
                {
                    "event": "inject_skip",
                    "reason": "nexus_core_missing",
                }
            )
            return []
        
        try:
            max_items = int(self.config.inject_max_items)
            threshold = float(self.config.inject_threshold)

            fetch_n = max_items
            if self.config.inject_dynamic_enabled:
                fetch_n = max(fetch_n, int(self.config.inject_dynamic_max_items))
            results = self._call_nexus("search_recall", user_message, fetch_n) or []
            if not results:
                self._append_metrics(
                    {
                        "event": "inject_empty",
                        "reason": reason,
                        "query_len": len(user_message or ""),
                    }
                )
            items: List[Dict[str, Any]] = []
            for r in results:
                metadata = getattr(r, "metadata", {}) or {}
                tags = self._normalize_tags(metadata)
                score = self._score_injected_item(float(getattr(r, "relevance", 0.0) or 0.0), tags, getattr(r, "source", ""))
                items.append(
                    {
                        "content": getattr(r, "content", ""),
                        "source": getattr(r, "source", ""),
                        "relevance": getattr(r, "relevance", 0.0),
                        "score": score,
                        "tags": tags,
                    }
                )

            max_items, threshold = self._dynamic_inject_params(reason, items)

            filtered = [
                item
                for item in items
                if float(item.get("score", item.get("relevance", 0.0))) >= threshold
            ]
            if self.config.inject_debug:
                sources = [r.get("source", "unknown") for r in filtered]
                sample = (filtered[0]["content"][: self.config.inject_debug_max_chars] if filtered else "")
                print(
                    f"[SmartContext] INJECT ok reason={reason} topk={len(filtered)}/{len(results)} "
                    f"threshold={threshold} sources={sources} sample={sample!r}"
                )
            retrieved = len(results)
            injected = len(filtered)
            ratio = (injected / retrieved) if retrieved else 0.0
            self._append_metrics(
                {
                    "event": "inject",
                    "reason": reason,
                    "retrieved": retrieved,
                    "injected": injected,
                    "ratio": round(ratio, 3),
                    "threshold": round(float(threshold), 3),
                    "max_items": int(max_items),
                }
            )
            
            graph_items = self._inject_graph_associations(user_message, reason)
            final = filtered + graph_items
            if self.config.inject_topk_only:
                def _score(item: Dict[str, Any]) -> float:
                    try:
                        return float(item.get("score", item.get("relevance", 0.0)))
                    except Exception:
                        return 0.0
                final = sorted(final, key=_score, reverse=True)[: max(1, int(max_items))]
            final = self._trim_injected_items(final)
            graph_ratio = (len(graph_items) / injected) if injected else 0.0
            self._append_metrics(
                {
                    "event": "graph_inject",
                    "reason": reason,
                    "graph_injected": len(graph_items),
                    "graph_ratio": round(graph_ratio, 3),
                }
            )
            self._record_inject_event(reason, len(final))
            self._record_inject_stats(reason, len(results), len(filtered), len(graph_items), threshold)
            return final
            
        except Exception as e:
            print(f"⚠️ 记忆注入失败: {e}")
            return []

    def _record_inject_event(self, reason: str, injected_count: int) -> None:
        if not self.config.adaptive_enabled:
            return
        self._inject_history.append(
            {
                "reason": reason,
                "count": int(injected_count),
            }
        )
        if len(self._inject_history) >= int(self.config.adaptive_window):
            self._tune_adaptive()

    def _record_inject_stats(
        self,
        reason: str,
        retrieved: int,
        injected: int,
        graph_injected: int,
        threshold: float,
    ) -> None:
        if not self.config.inject_stats_enabled:
            return
        self._inject_stats.append(
            {
                "reason": reason,
                "retrieved": int(retrieved),
                "injected": int(injected),
                "graph": int(graph_injected),
                "ratio": round((injected / retrieved), 3) if retrieved else 0.0,
                "threshold": round(float(threshold), 3),
            }
        )
        window = int(self.config.inject_stats_window)
        if window <= 0 or len(self._inject_stats) < window:
            return
        recent = self._inject_stats[-window:]
        count = len(recent)
        total_retrieved = sum(r.get("retrieved", 0) for r in recent)
        total_injected = sum(r.get("injected", 0) for r in recent)
        total_graph = sum(r.get("graph", 0) for r in recent)
        avg_ratio = (total_injected / total_retrieved) if total_retrieved else 0.0
        self._append_metrics(
            {
                "event": "inject_stats",
                "window": count,
                "retrieved": total_retrieved,
                "injected": total_injected,
                "graph_injected": total_graph,
                "avg_ratio": round(avg_ratio, 3),
            }
        )
        self._maybe_alert_inject_ratio(avg_ratio, count)

    def _maybe_alert_inject_ratio(self, avg_ratio: float, window: int) -> None:
        if not self.config.inject_ratio_alert_enabled:
            return
        threshold = float(self.config.inject_ratio_alert_threshold)
        if avg_ratio < threshold:
            self._inject_ratio_streak += 1
        else:
            self._inject_ratio_streak = 0
        if self._inject_ratio_streak >= int(self.config.inject_ratio_alert_streak):
            self._append_metrics(
                {
                    "event": "inject_ratio_alert",
                    "avg_ratio": round(avg_ratio, 3),
                    "threshold": round(threshold, 3),
                    "window": int(window),
                    "streak": int(self._inject_ratio_streak),
                }
            )
            if self.config.inject_debug:
                print(
                    f"[SmartContext] ALERT inject ratio low avg={avg_ratio:.2f} "
                    f"threshold={threshold:.2f} window={window}"
                )
        if self.config.inject_ratio_auto_tune:
            self._auto_tune_inject(avg_ratio)
        self._flush_pending_config_updates()

    def _auto_tune_inject(self, avg_ratio: float) -> None:
        step = float(self.config.inject_ratio_auto_tune_step)
        if avg_ratio <= 0 and step <= 0:
            return
        old_threshold = float(self.config.inject_threshold)
        new_threshold = max(self.config.adaptive_min_threshold, old_threshold - step)
        if new_threshold != old_threshold:
            self.config.inject_threshold = new_threshold
        old_max_items = int(self.config.inject_max_items)
        max_cap = int(self.config.inject_ratio_auto_tune_max_items)
        new_max_items = min(max_cap, max(old_max_items, old_max_items + 1))
        if new_max_items != old_max_items:
            self.config.inject_max_items = new_max_items
        self._append_metrics(
            {
                "event": "inject_auto_tune",
                "avg_ratio": round(avg_ratio, 3),
                "threshold_before": round(old_threshold, 3),
                "threshold_after": round(float(self.config.inject_threshold), 3),
                "max_items_before": old_max_items,
                "max_items_after": int(self.config.inject_max_items),
            }
        )
        self._persist_smart_context_config(
            {
                "inject_threshold": float(self.config.inject_threshold),
                "inject_max_items": int(self.config.inject_max_items),
            }
        )
        if self.config.inject_debug:
            print(
                f"[SmartContext] AUTO_TUNE inject threshold {old_threshold:.2f}->{self.config.inject_threshold:.2f} "
                f"max_items {old_max_items}->{self.config.inject_max_items}"
            )

    def _tune_adaptive(self) -> None:
        if not self._inject_history:
            return
        window = int(self.config.adaptive_window)
        if window <= 0:
            return
        recent = self._inject_history[-window:]
        success = sum(1 for r in recent if r.get("count", 0) > 0)
        ratio = success / float(len(recent))

        step = float(self.config.adaptive_step)
        new_threshold = self.config.inject_threshold
        if ratio < 0.35:
            new_threshold = min(self.config.adaptive_max_threshold, self.config.inject_threshold + step)
        elif ratio > 0.7:
            new_threshold = max(self.config.adaptive_min_threshold, self.config.inject_threshold - step)

        if new_threshold != self.config.inject_threshold:
            if self.config.inject_debug:
                print(
                    f"[SmartContext] ADAPT threshold {self.config.inject_threshold:.2f} -> {new_threshold:.2f} "
                    f"(ratio={ratio:.2f}, window={len(recent)})"
                )
            self.config.inject_threshold = new_threshold

    def _inject_graph_associations(self, user_message: str, reason: str) -> List[Dict]:
        if not (self._graph_enabled and self.config.graph_inject_enabled):
            return []
        if reason not in {"context_starved", "question", "technical_term", "keyword"}:
            return []

        keywords = self.extract_keywords(user_message)
        if not keywords:
            return []

        max_items = max(1, int(self.config.graph_max_items))
        evidence_max = max(0, int(self.config.graph_evidence_max_chars))
        out: List[Dict] = []
        for kw in keywords[: max_items]:
            edges = graph_related_with_evidence(kw, limit=max_items, evidence_limit=1)
            for e in edges:
                ev = ""
                evidence = e.get("evidence") or []
                if evidence:
                    ev = (evidence[0].get("text") or "")[:evidence_max]
                content = f"{e.get('subj')} {e.get('rel')} {e.get('obj')}"
                if ev:
                    content = f"{content} | 证据: {ev}"
                out.append(
                    {
                        "content": content,
                        "source": "graph",
                        "relevance": e.get("weight", 1.0),
                    }
                )
        if self.config.inject_debug and out:
            print(f"[SmartContext] GRAPH inject count={len(out)} keywords={keywords[:max_items]}")
        return out[: max_items]
    
    def generate_context_prompt(self, user_message: str) -> str:
        """
        生成上下文提示词
        """
        results = self.inject_memory(user_message)
        
        if not results:
            return ""
        
        parts = ["## 相关记忆", ""]
        
        for i, r in enumerate(results, 1):
            parts.append(f"【{i}】({r.get('source', '未知')} - {r.get('relevance', 0):.2f})")
            parts.append(r.get('content', '')[:200])
            parts.append("")
        
        return "\n".join(parts)
    
    # ===================== 功能 3: 压缩前抢救 (NOW.md) =====================
    
    def rescue_before_compress(self, conversation: str) -> Dict[str, Any]:
        """
        压缩前抢救
        
        从对话中提取关键信息并保存到 NOW.md
        """
        if not self.config.rescue_enabled:
            return {"skipped": True, "reason": "rescue_disabled"}
        
        result = {"decisions_rescued": 0, "goals_rescued": 0, "questions_rescued": 0, "saved": False}
        
        try:
            from .now_manager import NOWManager
            now = NOWManager()
            
            # 提取 #GOLD 标记
            if self.config.rescue_gold:
                gold_matches = re.findall(r'#GOLD[:\s]*(.+?)(?:\n|$)', conversation)
                for match in gold_matches:
                    if match.strip() and match.strip() not in now.state.get("decisions", []):
                        now.state.setdefault("decisions", []).append(match.strip())
                        result["decisions_rescued"] += 1
            
            # 提取关键决策
            if self.config.rescue_decisions:
                for keyword in ["决定", "选择", "采用", "使用"]:
                    if keyword in conversation:
                        idx = conversation.find(keyword)
                        if idx != -1:
                            context = conversation[max(0, idx-30):idx+70].strip()
                            if context not in now.state.get("next_actions", []):
                                now.state.setdefault("next_actions", []).append(context)
                                result["goals_rescued"] += 1
            
            # 提取待解决问题
            if self.config.rescue_next_actions:
                for match in re.findall(r'[?？](.+?)(?:\n|$)', conversation):
                    if match.strip() and len(match.strip()) > 5 and match.strip() not in now.state.get("open_questions", []):
                        now.state.setdefault("open_questions", []).append(match.strip())
                        result["questions_rescued"] += 1
            
            total = result["decisions_rescued"] + result["goals_rescued"] + result["questions_rescued"]
            if total > 0:
                now.save()
                result["saved"] = True
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def get_rescue_context(self) -> str:
        """获取抢救上下文"""
        try:
            from .now_manager import NOWManager
            return NOWManager().format_context()
        except:
            return ""
    
    def clear_rescue(self):
        """清空抢救状态"""
        try:
            from .now_manager import NOWManager
            NOWManager().clear()
        except:
            pass
    
    # ===================== 便捷函数 =====================

def store_conversation(conversation_id: str, user_message: str, ai_response: str) -> Dict:
    """存储对话摘要（便捷函数）"""
    from ..compat import nexus_init, nexus_add

    if not nexus_init():
        return {"error": "nexus init failed", "stored": False}

    def _extract_summary(text: str) -> str:
        json_match = re.search(r'```json\\s*\\n([\\s\\S]*?)\\n```', text)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                return data.get("本次核心产出", data.get("核心产出", ""))
            except json.JSONDecodeError:
                pass
        summary_match = re.search(r'## 📋 总结[^\\n]*\\n([\\s\\S]*?)(?=\\n\\n|$)', text)
        if summary_match:
            return summary_match.group(1).strip()
        return (text or "")[:100].strip()

    def _extract_keywords(text: str) -> List[str]:
        words = re.findall(r'\\b\\w+\\b', text.lower())
        stop_words = {
            '的', '了', '是', '在', '我', '你', '他', '这', '那',
            '和', '就', '都', '也', '会', '可以', '什么', '怎么',
            '如何', '有没有', '是不是', '能不能'
        }
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        return list(dict.fromkeys(keywords))[:5]

    def _extract_decisions(text: str) -> List[str]:
        if not text:
            return []
        blocks: List[str] = []
        json_match = re.search(r'```json\\s*\\n([\\s\\S]*?)\\n```', text)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                for key in ("本次核心产出", "核心产出", "决策上下文"):
                    val = data.get(key)
                    if isinstance(val, str) and val.strip():
                        blocks.append(val.strip())
            except json.JSONDecodeError:
                pass
        decision_keywords = ("决定", "选择", "采用", "使用", "结论", "方案", "策略", "切换", "改为")
        for raw in text.splitlines():
            line = raw.strip(" \\t-•")
            if not line:
                continue
            if "#GOLD" in line:
                line = re.sub(r".*#GOLD[:\\s]*", "", line).strip()
            if any(k in line for k in decision_keywords) and len(line) >= 6:
                blocks.append(line)
        seen = set()
        uniq = []
        for b in blocks:
            if b in seen:
                continue
            seen.add(b)
            uniq.append(b)
        return uniq[:3]

    def _extract_topics(text: str) -> List[str]:
        if not text:
            return []
        topics: List[str] = []
        for raw in text.splitlines():
            line = raw.strip(" \t-•")
            if not line:
                continue
            if line.startswith("## "):
                topics.append(line[3:].strip()[:60])
            if any(k in line for k in ("主题", "话题", "模块", "子系统", "项目")) and len(line) <= 80:
                topics.append(line)
        kws = _extract_keywords(text)
        if len(kws) >= 2:
            topics.append(" / ".join(kws[:3]))
        seen = set()
        uniq = []
        for t in topics:
            if t in seen:
                continue
            seen.add(t)
            uniq.append(t)
        return uniq[:3]

    summary = _extract_summary(ai_response)
    nexus_add(ai_response, f"对话 {conversation_id} - 原文", f"type:content,source:{conversation_id}")
    if summary:
        nexus_add(f"[摘要] {summary}", f"对话 {conversation_id} - 摘要", f"type:summary,source:{conversation_id}")

    keywords = _extract_keywords(user_message + " " + ai_response)
    if keywords:
        nexus_add(" ".join(keywords), f"对话 {conversation_id} - 关键词", f"type:keywords,source:{conversation_id}")

    decisions = _extract_decisions(user_message + "\\n" + ai_response)
    for idx, block in enumerate(decisions, 1):
        nexus_add(block, f"决策块 {conversation_id} - ({idx})", f"type:decision_block,source:{conversation_id}")

    topics = _extract_topics(user_message + "\\n" + ai_response)
    for idx, topic in enumerate(topics, 1):
        nexus_add(topic, f"主题块 {conversation_id} - ({idx})", f"type:topic_block,source:{conversation_id}")

    return {"stored": True, "conversation_id": conversation_id}


def inject_memory_context(user_message: str) -> str:
    """注入记忆上下文（便捷函数）"""
    from ..compat import nexus_init, nexus_recall

    if not nexus_init():
        return ""

    results = nexus_recall(user_message, n=3)
    if not results:
        return ""

    parts = ["## 相关记忆", ""]
    for i, r in enumerate(results, 1):
        parts.append(f"【{i}】({r.source} - {getattr(r, 'relevance', 0):.2f})")
        parts.append((r.content or "")[:200])
        parts.append("")
    return "\n".join(parts)


# ===================== 向后兼容 =====================

__all__ = [
    "SmartContextPlugin",
    "ContextCompressionConfig",
    "ConversationContext",
    "store_conversation",
    "inject_memory_context",
]
