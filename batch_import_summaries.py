#!/usr/bin/env python3
"""
批量导入摘要 JSON 文件到向量库
用于 cron 定期任务：nexus-summary-flush

步骤：
1. 检查 ~/.openclaw/logs/summaries/ 目录
2. 将所有待处理的摘要导入向量库
3. 清理已导入的文件

支持的 JSON 格式：
{
  "core_output": "string",
  "tech_points": ["string", ...],
  "code_pattern": "string",
  "decision_context": "string",
  "pitfall_record": "string",
  "applicable_scene": "string",
  "search_keywords": ["string", ...],
  "project关联": "string",
  "confidence": "high/medium/low",
  "source": "string (可选)"
}
"""

import os
import sys
import json
import glob
from datetime import datetime
from typing import Dict, Any, List

# 设置 DeepSea Nexus 路径
SKILLS_ROOT = os.path.expanduser("~/.openclaw/workspace/skills")
sys.path.insert(0, SKILLS_ROOT)

# 摘要文件目录
SUMMARIES_DIR = os.path.expanduser("~/.openclaw/logs/summaries")
# 批量导入日志
IMPORT_LOG = os.path.expanduser("~/.openclaw/logs/nexus-import.log")


def log(message: str, level: str = "INFO"):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] [{level}] {message}"
    print(log_msg)
    with open(IMPORT_LOG, 'a', encoding='utf-8') as f:
        f.write(log_msg + "\n")


def import_summary_file(filepath: str) -> bool:
    """导入单个摘要文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 调用 nexus_add_structured_summary
        from deepsea_nexus import nexus_add_structured_summary
        
        result = nexus_add_structured_summary(
            core_output=data.get("core_output", ""),
            tech_points=data.get("tech_points", []),
            code_pattern=data.get("code_pattern", ""),
            decision_context=data.get("decision_context", ""),
            pitfall_record=data.get("pitfall_record", ""),
            applicable_scene=data.get("applicable_scene", ""),
            search_keywords=data.get("search_keywords", []),
            project关联=data.get("project关联", ""),
            confidence=data.get("confidence", "medium"),
            source=data.get("source", os.path.basename(filepath))
        )
        
        if result and result.get("stored_count", 0) > 0:
            log(f"✅ 导入成功: {filepath} (存储 {result['stored_count']} 个文档)", "INFO")
            return True
        else:
            log(f"❌ 导入失败: {filepath} - 未存储任何文档", "ERROR")
            return False
            
    except Exception as e:
        log(f"❌ 导入失败: {filepath} - {str(e)}", "ERROR")
        import traceback
        log(traceback.format_exc(), "DEBUG")
        return False


def batch_import():
    """批量导入所有摘要文件"""
    log("=" * 50, "INFO")
    log("开始批量导入摘要", "INFO")
    
    # 检查目录是否存在
    if not os.path.exists(SUMMARIES_DIR):
        log(f"⚠️ 目录不存在: {SUMMARIES_DIR}", "WARNING")
        return {"total": 0, "imported": 0, "failed": 0}
    
    # 查找所有 JSON 文件
    pattern = os.path.join(SUMMARIES_DIR, "*.json")
    files = glob.glob(pattern)
    
    if not files:
        log("📭 没有找到待处理的摘要文件", "INFO")
        return {"total": 0, "imported": 0, "failed": 0}
    
    log(f"📦 待处理文件数: {len(files)}", "INFO")
    
    stats = {"total": len(files), "imported": 0, "failed": 0}
    
    for filepath in files:
        log(f"处理: {os.path.basename(filepath)}", "DEBUG")
        if import_summary_file(filepath):
            stats["imported"] += 1
            # 导入成功后删除文件
            try:
                os.remove(filepath)
                log(f"🗑️  已删除: {filepath}", "DEBUG")
            except Exception as e:
                log(f"⚠️  删除失败: {filepath} - {str(e)}", "WARNING")
        else:
            stats["failed"] += 1
    
    log(f"📊 导入完成: 总计 {stats['total']}, 成功 {stats['imported']}, 失败 {stats['failed']}", "INFO")
    log("=" * 50, "INFO")
    
    return stats


if __name__ == "__main__":
    try:
        stats = batch_import()
        # 输出简洁状态
        print(json.dumps(stats, ensure_ascii=False))
    except Exception as e:
        log(f"💥 批量导入异常: {str(e)}", "ERROR")
        import traceback
        log(traceback.format_exc(), "DEBUG")
        print(json.dumps({"total": 0, "imported": 0, "failed": 0, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)
