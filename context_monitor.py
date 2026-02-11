"""
上下文监控模块

功能：
- 监听上下文使用量
- 阈值检测 (>70% 触发警告)
- 集成 OpenClaw Hook 系统
"""

import re
from typing import Callable, Optional
from dataclasses import dataclass
from enum import Enum


class AlertLevel(Enum):
    """警告级别"""
    NORMAL = "normal"
    WARNING = "warning"  # >70%
    CRITICAL = "critical"  # >85%
    DANGER = "danger"  # >95%


@dataclass
class ContextStatus:
    """上下文状态"""
    level: AlertLevel
    usage_percent: float
    token_count: int
    max_tokens: int
    warning_message: str


class ContextMonitor:
    """
    上下文监控器
    
    使用方法:
    monitor = ContextMonitor(max_tokens=4000)
    monitor.on_warning(lambda status: print(f"警告: {status.warning_message}"))
    monitor.check(current_token_count)
    """
    
    # 阈值配置
    THRESHOLDS = {
        AlertLevel.WARNING: 0.70,   # 70%
        AlertLevel.CRITICAL: 0.85,  # 85%
        AlertLevel.DANGER: 0.95,    # 95%
    }
    
    def __init__(self, max_tokens: int = 4000):
        """
        初始化上下文监控器
        
        Args:
            max_tokens: 最大 token 限制
        """
        self.max_tokens = max_tokens
        self._warning_callbacks: list[Callable[[ContextStatus], None]] = []
        self._critical_callbacks: list[Callable[[ContextStatus], None]] = []
        self._last_status: Optional[ContextStatus] = None
        
    def register_warning_handler(self, callback: Callable[[ContextStatus], None]):
        """注册警告级别回调"""
        self._warning_callbacks.append(callback)
        
    def register_critical_handler(self, callback: Callable[[ContextStatus], None]):
        """注册严重级别回调"""
        self._critical_callbacks.append(callback)
        
    def check(self, token_count: int, buffer_size: int = 500) -> ContextStatus:
        """
        检查上下文使用状态
        
        Args:
            token_count: 当前 token 数量
            buffer_size: 保留缓冲 token 数
            
        Returns:
            ContextStatus: 当前状态
        """
        # 考虑保留缓冲
        effective_max = self.max_tokens - buffer_size
        usage_percent = token_count / effective_max if effective_max > 0 else 1.0
        
        # 确定级别
        if usage_percent >= self.THRESHOLDS[AlertLevel.DANGER]:
            level = AlertLevel.DANGER
        elif usage_percent >= self.THRESHOLDS[AlertLevel.CRITICAL]:
            level = AlertLevel.CRITICAL
        elif usage_percent >= self.THRESHOLDS[AlertLevel.WARNING]:
            level = AlertLevel.WARNING
        else:
            level = AlertLevel.NORMAL
            
        # 生成警告消息
        warning_msg = ""
        if level == AlertLevel.WARNING:
            warning_msg = f"⚠️ 上下文使用 {usage_percent*100:.1f}%，建议保存重要信息"
        elif level == AlertLevel.CRITICAL:
            warning_msg = f"🚨 上下文使用 {usage_percent*100:.1f}%，即将触发压缩"
        elif level == AlertLevel.DANGER:
            warning_msg = f"🔥 上下文 {usage_percent*100:.1f}%，立即抢救关键信息！"
            
        status = ContextStatus(
            level=level,
            usage_percent=usage_percent,
            token_count=token_count,
            max_tokens=self.max_tokens,
            warning_message=warning_msg
        )
        
        self._last_status = status
        
        # 触发回调
        self._trigger_callbacks(status)
        
        return status
    
    def _trigger_callbacks(self, status: ContextStatus):
        """触发注册的回调"""
        if status.level == AlertLevel.WARNING:
            for callback in self._warning_callbacks:
                try:
                    callback(status)
                except Exception:
                    pass
        elif status.level in (AlertLevel.CRITICAL, AlertLevel.DANGER):
            for callback in self._critical_callbacks:
                try:
                    callback(status)
                except Exception:
                    pass
    
    def should_rescue(self, token_count: int) -> bool:
        """判断是否应该触发抢救"""
        status = self.check(token_count)
        return status.level in (AlertLevel.CRITICAL, AlertLevel.DANGER)
    
    def get_remaining_tokens(self, token_count: int, buffer_size: int = 500) -> int:
        """获取剩余可用 token"""
        effective_max = self.max_tokens - buffer_size
        return max(0, effective_max - token_count)
    
    def estimate_collapse_distance(self, token_count: int, 
                                   avg_tokens_per_message: int = 200) -> int:
        """
        估算还能发送多少条消息
        
        Args:
            token_count: 当前 token
            avg_tokens_per_message: 平均每条消息 token 数
            
        Returns:
            int: 预计还能发送的消息数
        """
        remaining = self.get_remaining_tokens(token_count)
        return remaining // avg_tokens_per_message


class TokenEstimator:
    """Token 估算器"""
    
    # 中英文 token 估算系数
    CHINESE_CHARS_PER_TOKEN = 0.5  # 中文字符
    ENGLISH_CHARS_PER_TOKEN = 4    # 英文字符
    
    @classmethod
    def estimate(cls, text: str) -> int:
        """
        估算文本 token 数量
        
        Args:
            text: 输入文本
            
        Returns:
            int: 估算 token 数
        """
        # 简单估算：中文按字符，英文按空格分词
        chinese_count = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_count = len(re.sub(r'[\u4e00-\u9fff]', '', text))
        
        chinese_tokens = chinese_count / cls.CHINESE_CHARS_PER_TOKEN
        english_tokens = english_count / cls.ENGLISH_CHARS_PER_TOKEN
        
        return int(chinese_tokens + english_tokens)
    
    @classmethod
    def estimate_from_messages(self, messages) -> int:
        """
        从消息列表估算总 token
        
        Args:
            messages: 消息列表
            
        Returns:
            int: 总 token 估算
        """
        total = 0
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                total += cls.estimate(content)
            elif isinstance(content, list):
                for item in content:
                    if item.get("type") == "text":
                        total += cls.estimate(item.get("text", ""))
        return total


# 便捷函数
def check_context_usage(token_count: int, max_tokens: int = 4000) -> ContextStatus:
    """快速检查上下文使用状态"""
    monitor = ContextMonitor(max_tokens)
    return monitor.check(token_count)


if __name__ == "__main__":
    # 测试
    monitor = ContextMonitor(max_tokens=4000)
    
    # 注册回调
    def on_warning(status: ContextStatus):
        print(f"警告: {status.warning_message}")
        
    def on_critical(status: ContextStatus):
        print(f"严重: {status.warning_message}")
        
    monitor.register_warning_handler(on_warning)
    monitor.register_critical_handler(on_critical)
    
    # 测试场景
    test_tokens = [1000, 2000, 2800, 3400, 3800]
    
    for tokens in test_tokens:
        status = monitor.check(tokens)
        print(f"Token: {tokens} | 状态: {status.level.value} | {status.warning_message}")
