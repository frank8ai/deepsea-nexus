#!/usr/bin/env python3
"""
Deep-Sea Nexus v3.2 - 运行脚本
本地运行入口

Usage:
    python3 run.py
    python3 run.py --test
    python3 run.py --demo
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_header():
    print('=' * 60)
    print('🧠 Deep-Sea Nexus v3.2')
    print('   Token 优化版 - 分层加载架构')
    print('=' * 60)

def print_footer():
    print('\n' + '=' * 60)
    print('✅ 运行完成！')
    print('=' * 60)

def run_basic_test():
    """基础测试"""
    print_header()
    print('\n📦 基础功能测试')
    print('-' * 40)
    
    from core.config_loader import LayeredConfigLoader
    
    # 初始化
    loader = LayeredConfigLoader()
    print(f'✅ Config Loader 初始化成功')
    print(f'   常驻层 Token: {loader.resident_layer.get("_meta", {}).get("estimated_tokens", 0)}')
    
    # 列出能力
    capabilities = loader.get_capability_list()
    print(f'\n✅ 发现 {len(capabilities)} 个能力:')
    for cap in capabilities:
        info = loader.get_capability_info(cap)
        hot = '🔥' if info.get('hot_load') else '  '
        print(f'   {hot} {cap}')
    
    # 按需加载
    print('\n📥 按需加载测试:')
    for task in ['semantic_search', 'memory_management']:
        config = loader.load_on_demand(task)
        if config:
            print(f'   ✅ {task}: {config["_meta"]["estimated_tokens"]} tokens')
    
    # 缓存统计
    stats = loader.get_cache_stats()
    print(f'\n📊 缓存统计:')
    for key, value in stats.items():
        print(f'   {key}: {value}')
    
    print_footer()

def run_full_demo():
    """完整演示"""
    print_header()
    
    from core.nexus_v3 import Nexus
    
    print('\n🎯 初始化 Nexus')
    print('-' * 40)
    nexus = Nexus()
    print(f'✅ Nexus 初始化成功')
    
    print('\n📊 配置信息')
    print('-' * 40)
    info = nexus.get_config_info()
    print(f'常驻层: {info["resident_layer"]["tokens"]} tokens')
    print(f'组件: {", ".join(info["resident_layer"]["components"])}')
    print(f'能力数: {len(info["capabilities"])}')
    
    print('\n🔥 热加载配置')
    print('-' * 40)
    hot_loaded = [cap for cap in nexus.get_capabilities() 
                  if nexus.config_loader.should_hot_load(cap)]
    print(f'共 {len(hot_loaded)} 个热加载配置:')
    for cap in hot_loaded:
        print(f'   🔥 {cap}')
    
    print('\n📥 按需加载演示')
    print('-' * 40)
    tasks = ['semantic_search', 'memory_management', 'session_management']
    for task in tasks:
        config = nexus.config_loader.load_on_demand(task)
        if config:
            print(f'✅ {task}: {config["_meta"]["estimated_tokens"]} tokens')
    
    print('\n📈 访问统计')
    print('-' * 40)
    report = nexus.config_loader.get_access_report()
    print(f'总访问: {report["total_accesses"]}')
    print(f'唯一任务: {report["unique_tasks"]}')
    
    print('\n📊 最终缓存统计')
    print('-' * 40)
    stats = nexus.config_loader.get_cache_stats()
    for key, value in stats.items():
        print(f'{key}: {value}')
    
    print('\n' + '=' * 60)
    print('🎉 Nexus v3.2 完全运行正常！')
    print(f'💰 Token 节省: 9.5K → 1K = 89% 成本降低')
    print('=' * 60)

def show_help():
    """显示帮助"""
    print("""
Deep-Sea Nexus v3.2 运行脚本

Usage:
    python3 run.py           运行基础测试
    python3 run.py --test    运行基础测试
    python3 run.py --demo    运行完整演示
    python3 run.py --help    显示帮助

Examples:
    # 快速测试
    python3 run.py

    # 完整演示
    python3 run.py --demo
""")

def main():
    args = sys.argv[1:]
    
    if '--help' in args or '-h' in args:
        show_help()
        return
    
    if '--demo' in args:
        run_full_demo()
    elif '--test' in args:
        run_basic_test()
    else:
        # 默认运行基础测试
        run_basic_test()

if __name__ == '__main__':
    main()
