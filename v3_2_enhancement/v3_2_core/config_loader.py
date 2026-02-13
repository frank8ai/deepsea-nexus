"""
Deep-Sea Nexus v3.0 - Layered Config Loader
分层配置加载器 - 核心组件

常驻层：每次启动加载，常驻内存 (~3K tokens)
按需层：根据任务动态加载，支持缓存
"""

import json
import re
from pathlib import Path
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta

class SimpleYAML:
    """简单 YAML 解析器（避免依赖 PyYAML）"""
    
    @staticmethod
    def load(content: str) -> Dict:
        """解析简单的 YAML 文件"""
        result = {}
        current_key = None
        current_list = None
        indent_stack = [(0, result)]
        
        for line in content.split('\n'):
            if not line.strip() or line.strip().startswith('#'):
                continue
            
            # 计算缩进
            indent = len(line) - len(line.lstrip())
            
            # 找到当前层级的容器
            while indent_stack and indent_stack[-1][0] >= indent:
                indent_stack.pop()
            
            if not indent_stack:
                indent_stack = [(0, result)]
            
            current_container = indent_stack[-1][1]
            
            # 解析键值对
            if ':' in line:
                key, _, value = line.strip().partition(':')
                key = key.strip()
                value = value.strip()
                
                if value:
                    # 标量值
                    current_container[key] = SimpleYAML._parse_value(value)
                else:
                    # 可能是对象或列表的开始
                    current_container[key] = {}
                    indent_stack.append((indent, current_container[key]))
                    
            elif line.strip().startswith('- '):
                # 列表项
                if isinstance(current_container, dict):
                    # 找到最后一个键作为列表名
                    last_key = list(current_container.keys())[-1] if current_container else None
                    if last_key and not isinstance(current_container[last_key], list):
                        current_container[last_key] = []
                    if last_key:
                        value = line.strip()[2:].strip()
                        current_container[last_key].append(SimpleYAML._parse_value(value))
        
        return result
    
    @staticmethod
    def _parse_value(value: str):
        """解析 YAML 值"""
        value = value.strip()
        
        # 布尔值
        if value.lower() in ('true', 'yes', 'on'):
            return True
        if value.lower() in ('false', 'no', 'off'):
            return False
        
        # 数字
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            pass
        
        # 字符串（移除引号）
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            return value[1:-1]
        
        return value


class LayeredConfigLoader:
    """
    分层配置加载器
    
    设计目标：
    - 常驻层 < 3K tokens
    - 按需层用时加载，LRU 缓存
    - 自动统计访问模式，优化缓存策略
    """
    
    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path) if base_path else Path(__file__).parent.parent
        self.resident_layer = {}      # 常驻层配置
        self.on_demand_cache = {}     # 按需层缓存: {task_type: (config, expiry)}
        self.access_patterns = {}     # 访问模式统计
        self.cache_stats = {          # 缓存统计
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }
        
        # 加载常驻层
        self._load_resident_layer()
    
    def _load_resident_layer(self):
        """加载常驻层配置（启动时一次性加载）"""
        resident_path = self.base_path / "resident"
        
        # 加载路由表
        routing_file = resident_path / "routing_table.yaml"
        if routing_file.exists():
            with open(routing_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.resident_layer["routing"] = SimpleYAML.load(content)
        
        # 加载优先级规则
        priority_file = resident_path / "priority_rules.yaml"
        if priority_file.exists():
            with open(priority_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.resident_layer["priority"] = SimpleYAML.load(content)
        
        # 加载安全红线
        safety_file = resident_path / "safety_redlines.yaml"
        if safety_file.exists():
            with open(safety_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.resident_layer["safety"] = SimpleYAML.load(content)
        
        # 计算常驻层大小
        self._estimate_resident_size()
    
    def _estimate_resident_size(self):
        """估算常驻层 token 大小"""
        content = json.dumps(self.resident_layer, ensure_ascii=False)
        # 粗略估算：英文 ~4 chars/token，中文 ~2 chars/token
        estimated_tokens = len(content) // 3
        self.resident_layer["_meta"] = {
            "estimated_tokens": estimated_tokens,
            "loaded_at": datetime.now().isoformat()
        }
    
    def get_resident_layer(self) -> Dict[str, Any]:
        """获取常驻层配置"""
        return self.resident_layer
    
    def load_on_demand(self, task_type: str, force_reload: bool = False) -> Optional[Dict[str, Any]]:
        """
        按需加载特定任务的配置
        
        Args:
            task_type: 任务类型，如 "semantic_search"
            force_reload: 强制重新加载，忽略缓存
            
        Returns:
            配置字典，如果任务不存在返回 None
        """
        # 记录访问
        self._record_access(task_type)
        
        # 检查缓存
        if not force_reload and task_type in self.on_demand_cache:
            config, expiry = self.on_demand_cache[task_type]
            if datetime.now() < expiry:
                self.cache_stats["hits"] += 1
                return config
            else:
                # 缓存过期
                del self.on_demand_cache[task_type]
                self.cache_stats["evictions"] += 1
        
        # 从路由表获取配置路径
        routing = self.resident_layer.get("routing", {})
        capabilities = routing.get("capabilities", {})
        
        if task_type not in capabilities:
            return None
        
        capability = capabilities[task_type]
        config_file = capability.get("config_file")
        cache_ttl = capability.get("cache_ttl", 300)
        
        if not config_file:
            return None
        
        # 加载配置文件
        config_path = self.base_path / config_file
        if not config_path.exists():
            return None
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析配置
            config = {
                "_meta": {
                    "task_type": task_type,
                    "loaded_at": datetime.now().isoformat(),
                    "estimated_tokens": len(content) // 3,
                    "source_file": str(config_file)
                },
                "content": content
            }
            
            # 存入缓存
            expiry = datetime.now() + timedelta(seconds=cache_ttl)
            self.on_demand_cache[task_type] = (config, expiry)
            self.cache_stats["misses"] += 1
            
            return config
            
        except Exception as e:
            print(f"Error loading config for {task_type}: {e}")
            return None
    
    def _record_access(self, task_type: str):
        """记录访问模式"""
        if task_type not in self.access_patterns:
            self.access_patterns[task_type] = {
                "count": 0,
                "last_access": None,
                "first_access": datetime.now().isoformat()
            }
        
        self.access_patterns[task_type]["count"] += 1
        self.access_patterns[task_type]["last_access"] = datetime.now().isoformat()
    
    def get_capability_list(self) -> List[str]:
        """获取所有可用能力列表"""
        routing = self.resident_layer.get("routing", {})
        return list(routing.get("capabilities", {}).keys())
    
    def get_capability_info(self, task_type: str) -> Optional[Dict[str, Any]]:
        """获取特定能力的详细信息"""
        routing = self.resident_layer.get("routing", {})
        capabilities = routing.get("capabilities", {})
        return capabilities.get(task_type)
    
    def should_hot_load(self, task_type: str) -> bool:
        """判断是否应该热加载（常驻内存）"""
        info = self.get_capability_info(task_type)
        if not info:
            return False
        return info.get("hot_load", False)
    
    def preload_hot_configs(self):
        """预加载所有热加载配置"""
        for task_type in self.get_capability_list():
            if self.should_hot_load(task_type):
                self.load_on_demand(task_type)
                print(f"[Hot Load] {task_type}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        total = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = self.cache_stats["hits"] / total if total > 0 else 0
        
        return {
            **self.cache_stats,
            "hit_rate": f"{hit_rate:.1%}",
            "cached_items": len(self.on_demand_cache),
            "resident_tokens": self.resident_layer.get("_meta", {}).get("estimated_tokens", 0)
        }
    
    def get_access_report(self) -> Dict[str, Any]:
        """生成访问模式报告"""
        sorted_patterns = sorted(
            self.access_patterns.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )
        
        return {
            "total_accesses": sum(p["count"] for _, p in sorted_patterns),
            "unique_tasks": len(sorted_patterns),
            "top_tasks": [
                {"task": task, **stats}
                for task, stats in sorted_patterns[:5]
            ]
        }
    
    def clear_cache(self, task_type: Optional[str] = None):
        """清理缓存"""
        if task_type:
            if task_type in self.on_demand_cache:
                del self.on_demand_cache[task_type]
        else:
            self.on_demand_cache.clear()


# 全局单例
_config_loader = None

def get_config_loader(base_path: Optional[str] = None) -> LayeredConfigLoader:
    """获取配置加载器单例"""
    global _config_loader
    if _config_loader is None:
        _config_loader = LayeredConfigLoader(base_path)
    return _config_loader


# 便捷函数
def get_resident_config() -> Dict[str, Any]:
    """获取常驻层配置"""
    return get_config_loader().get_resident_layer()

def load_task_config(task_type: str) -> Optional[Dict[str, Any]]:
    """加载特定任务配置"""
    return get_config_loader().load_on_demand(task_type)

def list_capabilities() -> List[str]:
    """列出所有能力"""
    return get_config_loader().get_capability_list()


if __name__ == "__main__":
    # 测试
    loader = LayeredConfigLoader()
    
    print("=" * 50)
    print("Deep-Sea Nexus v3.0 - Config Loader Test")
    print("=" * 50)
    
    print("\n=== Resident Layer ===")
    print(f"Tokens: {loader.resident_layer.get('_meta', {}).get('estimated_tokens', 0)}")
    print(f"Capabilities: {loader.get_capability_list()}")
    
    print("\n=== Loading On-Demand ===")
    config = loader.load_on_demand("semantic_search")
    if config:
        print(f"Loaded: {config['_meta']['task_type']}")
        print(f"Tokens: {config['_meta']['estimated_tokens']}")
    
    print("\n=== Cache Stats ===")
    print(loader.get_cache_stats())
    
    print("\n=== All Capabilities ===")
    for cap in loader.get_capability_list():
        info = loader.get_capability_info(cap)
        hot = "🔥" if info.get("hot_load") else "  "
        print(f"  {hot} {cap}: {info.get('description', 'N/A')[:40]}...")
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("=" * 50)
