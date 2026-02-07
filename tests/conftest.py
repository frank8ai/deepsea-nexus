"""
Pytest 配置
"""
import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

import pytest


def pytest_configure(config):
    """Pytest 配置"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )


def pytest_collection_modifyitems(config, items):
    """修改测试项目"""
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(pytest.mark.slow)


@pytest.fixture(scope="session")
def nexus_config():
    """Nexus 配置fixture"""
    from src.config import NexusConfig
    return NexusConfig()


@pytest.fixture
def temp_dir(tmp_path):
    """临时目录fixture"""
    return tmp_path


@pytest.fixture
def sample_session_content():
    """示例 Session 内容"""
    return """---
uuid: 20260207092300
type: session
tags: [Python学习, 编程]
status: active
created: 2026-02-07T09:23:00
---

# Python学习

今天开始学习 Python。

## 第一节：基础语法

Python 是一门解释型语言。

#GOLD 使用 ChromaDB 作为向量库

继续学习列表...
"""
