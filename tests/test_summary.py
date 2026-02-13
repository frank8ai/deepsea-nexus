"""
测试用例 - 上下文摘要系统 v2.0

验证：
1. 结构化摘要解析
2. 向后兼容旧格式
3. 向量库存储
4. 检索精度
"""

import sys
import os
import json
from pathlib import Path

# 添加路径
SKILL_ROOT = Path(__file__).parent
sys.path.insert(0, str(SKILL_ROOT))

from auto_summary import SummaryParser, StructuredSummary, HybridStorage


class MockVectorStore:
    """模拟向量库（用于测试）"""
    
    def __init__(self):
        self.documents = []
    
    def add(self, content: str, title: str, tags: str = "") -> str:
        doc_id = f"doc_{len(self.documents)}"
        self.documents.append({
            "id": doc_id,
            "content": content,
            "title": title,
            "tags": tags,
        })
        return doc_id
    
    def search(self, query: str, limit: int = 5) -> list:
        # 简单模拟：返回所有文档
        return self.documents[:limit]


def test_structured_summary():
    """测试结构化摘要解析"""
    print("=" * 60)
    print("Test 1: 结构化摘要解析")
    print("=" * 60)
    
    parser = SummaryParser()
    
    test_response = """
Python 装饰器是一种修改函数行为的高级语法。

例如：
```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("调用前")
        result = func(*args, **kwargs)
        print("调用后")
        return result
    return wrapper
```

```json
{
  "本次核心产出": "学习 Python 装饰器的高级用法和执行顺序",
  "技术要点": ["装饰器语法", "@语法糖", "执行顺序"],
  "代码模式": "def decorator(func):\\n    def wrapper(*args,**kwargs):\\n        ...\\n    return wrapper",
  "决策上下文": "使用装饰器是因为需要在多个函数前后添加通用逻辑",
  "避坑记录": "装饰器执行顺序是从下到上，调用顺序是从上到下",
  "适用场景": "日志记录、权限检查、缓存等横切关注点",
  "搜索关键词": ["python", "装饰器", "decorator", "语法"],
  "项目关联": "Python 学习",
  "置信度": "high"
}
```
"""
    
    reply, summary = parser.parse(test_response)
    
    assert summary is not None, "摘要不应为 None"
    assert isinstance(summary, StructuredSummary), "应该是结构化摘要"
    
    print(f"✅ 核心产出: {summary.core_output}")
    print(f"✅ 技术要点: {summary.tech_points}")
    print(f"✅ 代码模式: {summary.code_pattern[:50]}...")
    print(f"✅ 置信度: {summary.confidence}")
    
    # 验证字段
    assert "装饰器" in summary.core_output
    assert len(summary.tech_points) == 3
    assert summary.confidence == "high"
    
    print("✅ 结构化摘要解析测试通过")


def test_legacy_compatibility():
    """测试向后兼容"""
    print("\n" + "=" * 60)
    print("Test 2: 向后兼容旧格式")
    print("=" * 60)
    
    parser = SummaryParser()
    
    # 测试旧格式
    test_old = """
这是旧格式的回复。

---SUMMARY---
学习 Python 装饰器的基本用法
---END---
"""
    
    reply, summary = parser.parse(test_old)
    
    assert summary is not None, "旧格式摘要不应为 None"
    assert isinstance(summary, StructuredSummary), "应该转换为结构化摘要"
    assert "装饰器" in summary.core_output
    assert summary.confidence == "low", "旧格式置信度应为 low"
    
    print(f"✅ 旧格式核心产出: {summary.core_output}")
    print(f"✅ 置信度: {summary.confidence}")
    
    print("✅ 向后兼容测试通过")


def test_summary_to_searchable():
    """测试摘要转可搜索文本"""
    print("\n" + "=" * 60)
    print("Test 3: 摘要转可搜索文本")
    print("=" * 60)
    
    summary = StructuredSummary(
        core_output="学习 Python 装饰器的高级用法",
        tech_points=["装饰器语法", "执行顺序"],
        code_pattern="def decorator(func):...",
        decision_context="选择装饰器是因为代码复用",
        pitfall_record="注意执行顺序",
        applicable_scene="日志记录、权限检查",
        search_keywords=["python", "decorator"],
        project关联="Python 学习",
        confidence="high"
    )
    
    searchable = summary.to_searchable_text()
    print(f"可搜索文本: {searchable[:100]}...")
    
    # 验证所有字段都被包含
    assert "装饰器" in searchable
    assert "python" in searchable
    assert "decorator" in searchable
    assert "Python 学习" in searchable
    
    print("✅ 可搜索文本转换测试通过")


def test_hybrid_storage():
    """测试混合存储"""
    print("\n" + "=" * 60)
    print("Test 4: 混合存储")
    print("=" * 60)
    
    mock_store = MockVectorStore()
    storage = HybridStorage(mock_store)
    
    conversation_id = "test_001"
    test_response = """
这是一个测试回复，包含代码和结构化摘要。

```json
{
  "本次核心产出": "测试混合存储功能",
  "技术要点": ["测试用例", "验证存储"],
  "代码模式": "mock_store.add(content, title, tags)",
  "决策上下文": "使用 Mock 是为了测试隔离",
  "避坑记录": "确保清理测试数据",
  "适用场景": "单元测试",
  "搜索关键词": ["测试", "存储", "验证"],
  "项目关联": "单元测试",
  "置信度": "high"
}
```
"""
    
    result = storage.process_and_store(conversation_id, test_response)
    
    print(f"存储文档数: {result['stored_count']}")
    print(f"摘要数据类型: {result['summary_type']}")
    
    # 验证：应该存储原文 + 结构化摘要 + 元数据 + 关键词 = 4 个文档
    assert result["stored_count"] == 4, f"期望 4，实际 {result['stored_count']}"
    assert result["has_summary"] == True
    
    print(f"✅ 存储原文: 1")
    print(f"✅ 存储结构化摘要: 1")
    print(f"✅ 存储元数据: 1")
    print(f"✅ 存储关键词: 1")
    
    print("✅ 混合存储测试通过")


def test_tags_generation():
    """测试标签生成"""
    print("\n" + "=" * 60)
    print("Test 5: 标签生成")
    print("=" * 60)
    
    summary = StructuredSummary(
        core_output="测试标签生成",
        tech_points=["测试", "标签"],
        search_keywords=["python", "test", "tags"],
        confidence="medium"
    )
    
    tags = summary.to_tags()
    print(f"生成的标签: {tags}")
    
    assert tags == "python,test,tags"
    
    print("✅ 标签生成测试通过")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("🧪 上下文摘要系统 v2.0 测试套件")
    print("=" * 60)
    
    tests = [
        test_structured_summary,
        test_legacy_compatibility,
        test_summary_to_searchable,
        test_hybrid_storage,
        test_tags_generation,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__} 失败: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} 错误: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
