"""
Deep-Sea Nexus v3.0 - Main Entry Point
主入口 - 分层加载架构

Usage:
    from deepsea_nexus import Nexus
    nexus = Nexus()
    results = nexus.recall("query")
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass

from core.config_loader import (
    get_config_loader,
    get_resident_config,
    load_task_config,
    list_capabilities
)

@dataclass
class RecallResult:
    """检索结果"""
    content: str
    source: str
    relevance: float
    metadata: Dict[str, Any]


class Nexus:
    """
    Deep-Sea Nexus v3.0 主类
    
    特性：
    - 常驻层自动加载 (~3K tokens)
    - 按需层智能缓存
    - 自动路由到正确的配置
    """
    
    def __init__(self, base_path: Optional[str] = None):
        """
        初始化 Nexus
        
        自动加载常驻层配置（约 3K tokens）
        """
        self.config_loader = get_config_loader(base_path)
        self.resident_config = get_resident_config()
        self._nexus_core = None  # 延迟加载
        self._initialized = False
        
        # 预加载热配置
        self.config_loader.preload_hot_configs()
    
    def _ensure_initialized(self):
        """确保核心模块已初始化（按需加载）"""
        if not self._initialized:
            # 这里会加载 nexus_core 模块
            # 为了避免循环导入，延迟加载
            try:
                import sys
                sys.path.insert(0, str(Path(__file__).parent.parent / "deepsea-nexus"))
                from nexus_core import nexus_init
                nexus_init()
                self._initialized = True
            except Exception as e:
                print(f"Warning: Could not initialize nexus_core: {e}")
    
    def recall(self, query: str, limit: int = 5, 
               filters: Optional[Dict] = None,
               min_relevance: float = 0.0) -> List[RecallResult]:
        """
        语义检索
        
        自动加载 semantic_search 配置
        """
        # 加载按需配置
        config = load_task_config("semantic_search")
        
        self._ensure_initialized()
        
        try:
            from nexus_core import nexus_recall
            raw_results = nexus_recall(query, limit)
            
            results = []
            for r in raw_results:
                if r.relevance >= min_relevance:
                    results.append(RecallResult(
                        content=r.content,
                        source=r.source,
                        relevance=r.relevance,
                        metadata=getattr(r, 'metadata', {})
                    ))
            
            return results
            
        except Exception as e:
            print(f"Error in recall: {e}")
            return []
    
    def add(self, content: str, title: Optional[str] = None, 
            tags: Optional[str] = None) -> Optional[str]:
        """
        添加记忆
        
        自动加载 memory_management 配置
        """
        config = load_task_config("memory_management")
        
        self._ensure_initialized()
        
        try:
            from nexus_core import nexus_add
            return nexus_add(content, title, tags)
        except Exception as e:
            print(f"Error in add: {e}")
            return None
    
    def add_structured_summary(self, **kwargs) -> Optional[str]:
        """
        添加结构化摘要
        
        参数：
            core_output: 本次核心产出
            tech_points: 技术要点列表
            code_pattern: 代码模式
            decision_context: 决策上下文
            pitfalls: 避坑记录
            applicable_scenes: 适用场景
            keywords: 搜索关键词列表
            project: 项目关联
            confidence: 置信度
        """
        config = load_task_config("summary_generation")
        
        self._ensure_initialized()
        
        try:
            from nexus_core import nexus_add_structured_summary
            return nexus_add_structured_summary(**kwargs)
        except Exception as e:
            print(f"Error in add_structured_summary: {e}")
            return None
    
    @property
    def session(self):
        """
        会话管理子模块
        
        自动加载 session_management 配置
        """
        config = load_task_config("session_management")
        
        if not hasattr(self, '_session_mgr'):
            try:
                from session_manager import SessionManager
                self._session_mgr = SessionManager()
            except Exception as e:
                print(f"Error loading session manager: {e}")
                return None
        
        return self._session_mgr
    
    @property
    def flush(self):
        """
        Flush 管理子模块
        
        自动加载 flush_management 配置
        """
        config = load_task_config("flush_management")
        
        if not hasattr(self, '_flush_mgr'):
            try:
                from flush_manager import FlushManager
                self._flush_mgr = FlushManager()
            except Exception as e:
                print(f"Error loading flush manager: {e}")
                return None
        
        return self._flush_mgr
    
    def get_stats(self) -> Dict[str, Any]:
        """获取系统统计"""
        self._ensure_initialized()
        
        try:
            from nexus_core import nexus_stats
            core_stats = nexus_stats()
        except:
            core_stats = {}
        
        return {
            "core": core_stats,
            "config": self.config_loader.get_cache_stats(),
            "resident_tokens": self.resident_config.get("_meta", {}).get("estimated_tokens", 0)
        }
    
    def get_capabilities(self) -> List[str]:
        """获取所有可用能力"""
        return list_capabilities()
    
    def get_config_info(self) -> Dict[str, Any]:
        """获取配置信息"""
        return {
            "resident_layer": {
                "tokens": self.resident_config.get("_meta", {}).get("estimated_tokens", 0),
                "components": list(self.resident_config.keys())
            },
            "capabilities": self.get_capabilities(),
            "cache_stats": self.config_loader.get_cache_stats()
        }


# 便捷函数（兼容旧版 API）
def nexus_recall(query: str, limit: int = 5):
    """语义检索（便捷函数）"""
    nexus = Nexus()
    return nexus.recall(query, limit)

def nexus_add(content: str, title: str = None, tags: str = None):
    """添加记忆（便捷函数）"""
    nexus = Nexus()
    return nexus.add(content, title, tags)


def demo():
    """演示分层加载"""
    print("=" * 50)
    print("Deep-Sea Nexus v3.0 - Token 优化版")
    print("=" * 50)
    
    nexus = Nexus()
    
    print("\n📊 配置信息")
    print("-" * 30)
    info = nexus.get_config_info()
    print(f"常驻层大小: {info['resident_layer']['tokens']} tokens")
    print(f"常驻组件: {', '.join(info['resident_layer']['components'])}")
    print(f"可用能力: {len(info['capabilities'])} 个")
    
    print("\n📋 能力列表")
    print("-" * 30)
    for cap in info['capabilities']:
        print(f"  • {cap}")
    
    print("\n🚀 按需加载演示")
    print("-" * 30)
    
    # 加载语义搜索配置
    config = load_task_config("semantic_search")
    if config:
        print(f"✅ semantic_search: {config['_meta']['estimated_tokens']} tokens")
    
    # 加载会话管理配置
    config = load_task_config("session_management")
    if config:
        print(f"✅ session_management: {config['_meta']['estimated_tokens']} tokens")
    
    print("\n📈 缓存统计")
    print("-" * 30)
    stats = nexus.config_loader.get_cache_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 50)
    print("分层加载演示完成！")
    print("=" * 50)


if __name__ == "__main__":
    from pathlib import Path
    demo()
