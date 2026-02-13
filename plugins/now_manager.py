#!/usr/bin/env python3
"""
NOW.md - 压缩前抢救机制

功能：
- 压缩前自动保存当前目标
- 保存活跃线程和上下文
- 下一步行动
- 压缩后自动恢复

基于 Moltbook 最佳实践：
- RenBot: "Pre-compaction lifeboat: maintain a tiny NOW.md"

集成到 v3.1 Smart Context：
- 在 compress_before 之前调用
- 提取 #GOLD、关键决策
- 保存到 NOW.md
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional


class NOWManager:
    """
    NOW.md 抢救管理器
    
    使用方法:
    now = NOWManager()
    
    # 保存当前状态
    now.save(
        current_goal="完成Python项目",
        active_threads=["项目A", "项目B"],
        next_actions=["写测试", "提交代码"],
        open_questions=["架构设计是否合理?"]
    )
    
    # 压缩后恢复
    state = now.load()
    """
    
    def __init__(self, path: str = None):
        self.path = path or os.path.expanduser("~/.openclaw/workspace/NOW.md")
        self.state = self._load()
    
    def _load(self) -> Dict:
        """加载状态"""
        if not os.path.exists(self.path):
            return {}
        
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            state = {
                "updated": None,
                "current_goal": "",
                "active_threads": [],
                "next_actions": [],
                "open_questions": [],
                "decisions": [],
                "context_notes": ""
            }
            
            for line in content.split('\n'):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # 解析 KEY: VALUE 格式
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    value = value.strip()
                    
                    if key == 'updated':
                        state['updated'] = value
                    elif key == 'current_goal':
                        state['current_goal'] = value
                    elif key == 'active_threads':
                        state['active_threads'] = [v.strip() for v in value.split('|') if v.strip()]
                    elif key == 'next_actions':
                        state['next_actions'] = [v.strip() for v in value.split('|') if v.strip()]
                    elif key == 'open_questions':
                        state['open_questions'] = [v.strip() for v in value.split('|') if v.strip()]
                    elif key == 'decisions':
                        state['decisions'] = [v.strip() for v in value.split('|') if v.strip()]
            
            # 查找上下文笔记
            if '---' in content:
                state['context_notes'] = content.split('---')[-1].strip()
            
            return state
            
        except Exception as e:
            print(f"加载 NOW.md 失败: {e}")
            return {}
    
    def save(
        self,
        current_goal: str = "",
        active_threads: List[str] = None,
        next_actions: List[str] = None,
        open_questions: List[str] = None,
        decisions: List[str] = None,
        context_notes: str = ""
    ):
        """
        保存当前状态
        
        Args:
            current_goal: 当前目标
            active_threads: 活跃线程/项目
            next_actions: 下一步行动
            open_questions: 待解决问题
            decisions: 已做决定
            context_notes: 其他上下文注释
        """
        self.state = {
            "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "current_goal": current_goal or self.state.get("current_goal", ""),
            "active_threads": active_threads or self.state.get("active_threads", []),
            "next_actions": next_actions or self.state.get("next_actions", []),
            "open_questions": open_questions or self.state.get("open_questions", []),
            "decisions": decisions or self.state.get("decisions", []),
            "context_notes": context_notes or self.state.get("context_notes", "")
        }
        
        # 写入文件
        with open(self.path, 'w', encoding='utf-8') as f:
            f.write("# NOW.md - 抢救文件\n")
            f.write("---\n")
            f.write(f"updated: {self.state['updated']}\n")
            f.write("---\n\n")
            
            f.write("## 当前目标\n")
            f.write(f"current_goal: {self.state['current_goal']}\n\n")
            
            f.write("## 活跃线程\n")
            f.write(f"active_threads: {' | '.join(self.state['active_threads'])}\n\n")
            
            f.write("## 下一步行动\n")
            f.write(f"next_actions: {' | '.join(self.state['next_actions'])}\n\n")
            
            f.write("## 待解决问题\n")
            f.write(f"open_questions: {' | '.join(self.state['open_questions'])}\n\n")
            
            f.write("## 已做决定\n")
            f.write(f"decisions: {' | '.join(self.state['decisions'])}\n\n")
            
            if self.state['context_notes']:
                f.write("---\n")
                f.write(self.state['context_notes'])
        
        print(f"✅ 已保存 NOW.md")
    
    def load(self) -> Dict:
        """加载状态"""
        return self.state
    
    def clear(self):
        """清空状态"""
        self.state = {
            "updated": None,
            "current_goal": "",
            "active_threads": [],
            "next_actions": [],
            "open_questions": [],
            "decisions": [],
            "context_notes": ""
        }
        
        if os.path.exists(self.path):
            os.remove(self.path)
        
        print("🗑️ 已清空 NOW.md")
    
    def format_context(self) -> str:
        """格式化为可注入上下文"""
        state = self.state
        if not state.get('current_goal') and not state.get('active_threads'):
            return ""
        
        lines = ["**🔔 抢救上下文:**\n"]
        
        if state.get('current_goal'):
            lines.append(f"🎯 当前目标: {state['current_goal']}")
        
        if state.get('active_threads'):
            lines.append(f"📌 活跃线程: {' | '.join(state['active_threads'])}")
        
        if state.get('next_actions'):
            lines.append(f"➡️ 下一步: {' | '.join(state['next_actions'])}")
        
        if state.get('open_questions'):
            lines.append(f"❓ 待解决问题: {' | '.join(state['open_questions'])}")
        
        if state.get('decisions'):
            lines.append(f"✅ 已做决定: {' | '.join(state['decisions'])}")
        
        if state.get('context_notes'):
            lines.append(f"\n📝 备注:\n{state['context_notes']}")
        
        return '\n'.join(lines)
    
    def extract_from_conversation(self, conversation: str) -> Dict:
        """
        从对话中提取抢救信息
        
        提取：
        - #GOLD 标记的内容
        - 关键决策
        - 下一步行动
        """
        import re
        
        extracted = {
            "decisions": [],
            "goals": [],
            "questions": []
        }
        
        # 提取 #GOLD 标记
        gold_matches = re.findall(r'#GOLD[:\s]*(.+?)(?:\n|$)', conversation)
        for match in gold_matches:
            if match.strip():
                extracted["decisions"].append(match.strip())
        
        # 提取决策关键词
        decision_keywords = ["决定", "选择", "采用", "使用"]
        for keyword in decision_keywords:
            if keyword in conversation:
                # 尝试提取上下文
                idx = conversation.find(keyword)
                if idx != -1:
                    context = conversation[max(0, idx-50):idx+50]
                    extracted["goals"].append(context.strip())
        
        # 提取待解决问题
        question_matches = re.findall(r'[?？](.+?)(?:\n|$)', conversation)
        for match in question_matches:
            if match.strip() and len(match.strip()) > 5:
                extracted["questions"].append(match.strip())
        
        return extracted
    
    def rescue_before_compress(self, conversation: str) -> Dict:
        """
        压缩前抢救
        
        从对话中提取关键信息并保存
        
        Args:
            conversation: 对话内容
            
        Returns:
            抢救结果
        """
        extracted = self.extract_from_conversation(conversation)
        
        result = {
            "decisions_rescued": 0,
            "goals_rescued": 0,
            "questions_rescued": 0,
            "saved": False
        }
        
        # 合并到当前状态
        if extracted["decisions"]:
            existing = self.state.get("decisions", [])
            for d in extracted["decisions"]:
                if d not in existing:
                    existing.append(d)
            self.state["decisions"] = existing
            result["decisions_rescued"] = len(extracted["decisions"])
        
        if extracted["goals"]:
            existing = self.state.get("next_actions", [])
            for g in extracted["goals"]:
                if g not in existing:
                    existing.append(g)
            self.state["next_actions"] = existing
            result["goals_rescued"] = len(extracted["goals"])
        
        if extracted["questions"]:
            existing = self.state.get("open_questions", [])
            for q in extracted["questions"]:
                if q not in existing:
                    existing.append(q)
            self.state["open_questions"] = existing
            result["questions_rescued"] = len(extracted["questions"])
        
        # 保存
        if result["decisions_rescued"] + result["goals_rescued"] + result["questions_rescued"] > 0:
            self.save()
            result["saved"] = True
        
        return result
    
    def report(self) -> str:
        """生成报告"""
        state = self.state
        
        lines = [
            "=" * 50,
            "🔔 NOW.md 抢救状态",
            "=" * 50,
            f"更新时间: {state.get('updated', '未更新')}",
            "",
        ]
        
        if state.get('current_goal'):
            lines.append(f"🎯 {state['current_goal']}")
        
        if state.get('active_threads'):
            lines.append(f"📌 活跃: {' | '.join(state['active_threads'])}")
        
        if state.get('next_actions'):
            lines.append(f"➡️ 下一步: {' | '.join(state['next_actions'])}")
        
        lines.append("=" * 50)
        
        return '\n'.join(lines)


# ===================== CLI =====================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="🔔 NOW.md 抢救机制")
    parser.add_argument('--load', action='store_true', help='加载状态')
    parser.add_argument('--save', action='store_true', help='保存状态')
    parser.add_argument('--clear', action='store_true', help='清空状态')
    parser.add_argument('--context', action='store_true', help='格式化为上下文')
    parser.add_argument('--rescue', type=str, help='从对话抢救')
    parser.add_argument('--goal', '-g', help='当前目标')
    parser.add_argument('--threads', '-t', help='活跃线程 (用|分隔)')
    parser.add_argument('--actions', '-a', help='下一步行动 (用|分隔)')
    parser.add_argument('--questions', '-q', help='待解决问题 (用|分隔)')
    parser.add_argument('--decisions', '-d', help='已做决定 (用|分隔)')    
    args = parser.parse_args()
    
    now = NOWManager()
    
    if args.load:
        print(now.report())
    elif args.clear:
        now.clear()
    elif args.context:
        print(now.format_context())
    elif args.rescue:
        result = now.rescue_before_compress(args.rescue)
        print(f"抢救结果: {result}")
    elif args.save:
        threads = args.threads.split('|') if args.threads else []
        actions = args.actions.split('|') if args.actions else []
        questions = args.questions.split('|') if args.questions else []
        decisions = args.decisions.split('|') if args.decisions else []
        
        now.save(
            current_goal=args.goal or "",
            active_threads=threads,
            next_actions=actions,
            open_questions=questions,
            decisions=decisions
        )
    else:
        # 默认显示状态
        print(now.report())


if __name__ == '__main__':
    main()
