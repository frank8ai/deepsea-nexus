#!/usr/bin/env python3
"""
Deep-Sea Nexus Skills System
可组合的AI能力库

参考 TELOS Skills 设计，实现：
- 可命名的 Skills（通过 /skill-name 调用）
- 可参数化的任务执行
- Skills 可相互调用
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass


@dataclass
class Skill:
    """Skill 定义"""
    name: str
    description: str
    trigger: str  # /skill-name
    parameters: Dict[str, str]
    template: str
    category: str
    examples: List[str]


class SkillsSystem:
    """Skills 管理与执行系统"""
    
    def __init__(self, skills_path: str = None):
        self.skills_path = Path(skills_path or Path(__file__).parent / "skills")
        self.skills: Dict[str, Skill] = {}
        self._load_skills()
    
    def _load_skills(self):
        """加载所有Skills"""
        for skill_dir in self.skills_path.iterdir():
            if skill_dir.is_dir():
                skill_file = skill_dir / "skill.json"
                if skill_file.exists():
                    with open(skill_file) as f:
                        data = json.load(f)
                        skill = Skill(**data)
                        self.skills[skill.trigger] = skill
    
    def list_skills(self) -> List[Dict]:
        """列出所有可用Skills"""
        return [
            {
                "trigger": s.trigger,
                "name": s.name,
                "description": s.description,
                "category": s.category,
                "examples": s.examples
            }
            for s in self.skills.values()
        ]
    
    def execute(self, trigger: str, arguments: str = "") -> str:
        """执行指定Skill"""
        skill = self.skills.get(trigger)
        if not skill:
            return f"Skill not found: {trigger}"
        
        # 渲染模板
        prompt = skill.template
        if arguments:
            # 简单替换参数
            prompt = prompt.replace("{input}", arguments)
        
        return prompt


# 预定义 Skills

SKILLS = {
    "pr-review": {
        "name": "PR Review",
        "description": "审查 GitHub Pull Request",
        "trigger": "/pr-review",
        "parameters": {"pr_number": "PR编号"},
        "category": "development",
        "examples": ["/pr-review 123", "/pr-review 456"],
        "template": """请审查这个 Pull Request：

PR 编号: {pr_number}

请检查：
1. 代码质量 - 是否有潜在bug？
2. 风格一致性 - 是否符合项目规范？
3. 安全性 - 是否有安全风险？
4. 测试覆盖 - 是否有足够的测试？
5. 文档 - 是否需要更新文档？

请给出详细的审查意见。
"""
    },
    "commit-gen": {
        "name": "Generate Commit Message",
        "description": "智能生成 Git Commit Message",
        "trigger": "/commit",
        "parameters": {},
        "category": "git",
        "examples": ["/commit", "/commit --type feat"],
        "template": """根据以下 Git diff，生成一个规范的 commit message：

要求：
- 使用 Conventional Commits 格式
- 简洁描述变更内容
- 包含变更原因（如果非显而易见）

请生成 commit message：
"""
    },
    "analyze-logs": {
        "name": "Analyze Logs",
        "description": "分析日志文件中的错误",
        "trigger": "/analyze-logs",
        "parameters": {"file_path": "日志文件路径"},
        "category": "debug",
        "examples": ["/analyze-logs error", "/analyze-logs /var/log/app.log"],
        "template": """分析以下日志文件，识别错误和异常模式：

日志文件: {file_path}

请提供：
1. 错误摘要（错误类型、频率）
2. 关键错误详情
3. 可能的根因分析
4. 修复建议

日志内容：
"""
    },
    "explain-code": {
        "name": "Explain Code",
        "description": "详细解释代码文件",
        "trigger": "/explain-code",
        "parameters": {"file_path": "代码文件路径"},
        "category": "development",
        "examples": ["/explain-code main.py", "/explain-code src/utils.ts"],
        "template": """请详细解释以下代码文件：

文件路径: {file_path}

请覆盖：
1. 代码整体功能概述
2. 主要函数/类的作用
3. 关键逻辑的逐行解释
4. 潜在的改进点

代码内容：
"""
    }
}


def install_skill(skill_name: str):
    """安装预定义Skill"""
    if skill_name not in SKILLS:
        print(f"Skill not found: {skill_name}")
        return
    
    skill_dir = Path(__file__).parent / "skills" / skill_name
    skill_dir.mkdir(exist_ok=True)
    
    # 创建 skill.json
    with open(skill_dir / "skill.json", "w") as f:
        json.dump(SKILLS[skill_name], f, indent=2)
    
    print(f"Installed skill: {skill_name}")


def install_all_skills():
    """安装所有预定义Skills"""
    for skill_name in SKILLS.keys():
        install_skill(skill_name)


if __name__ == "__main__":
    print("Deep-Sea Nexus Skills System")
    print("=" * 40)
    
    skills = SkillsSystem()
    print(f"Skills path: {skills.skills_path}")
    print(f"Loaded skills: {len(skills.skills)}")
    
    print("\\nInstalling example skills...")
    install_all_skills()
    
    print("\\nAvailable skills:")
    for skill in skills.list_skills():
        print(f"  {skill['trigger']:15} - {skill['name']}")
    
    print("\\nSkills installed successfully!")
