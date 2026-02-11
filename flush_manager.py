"""
自动 Flush 模块

功能：
- 定时归档旧会话
- 清理低活跃 chunks
- 按时间策略管理存储
- 压缩归档功能

F5. 自动 Flush
"""

import os
import shutil
import json
import gzip
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import yaml


class FlushManager:
    """Flush 管理器"""
    
    def __init__(self, base_path: str = None, config: Dict = None):
        """
        初始化 Flush 管理器
        
        Args:
            base_path: 记忆库根路径
            config: 配置项
        """
        if base_path is None:
            self.base_path = os.path.expanduser("~/.openclaw/workspace/memory")
        else:
            self.base_path = base_path
        
        # 默认配置
        self.config = {
            "enabled": True,
            "archive_time": "03:00",  # 每日凌晨 3 点
            "archive_monthly": True,
            "archive_dir": "archive",
            "keep_active_days": 30,   # 活跃会话保留 30 天
            "keep_archived_days": 90, # 归档会话保留 90 天
            "min_chunks_to_archive": 5,  # 至少 5 个 chunks 才归档
            "compress_enabled": True,    # 启用压缩
        }
        
        # 合并配置
        if config:
            self.config.update(config)
        
        # 确保归档目录存在
        self.archive_path = os.path.join(self.base_path, self.config["archive_dir"])
        os.makedirs(self.archive_path, exist_ok=True)
    
    def should_archive(self, session_info: Dict) -> bool:
        """
        判断会话是否应该归档
        
        Args:
            session_info: 会话信息
            
        Returns:
            bool: 是否应该归档
        """
        # 检查 chunks 数量
        if session_info.get("chunk_count", 0) < self.config["min_chunks_to_archive"]:
            return False
        
        # 检查最后活跃时间
        last_active = session_info.get("last_active", "")
        if last_active:
            try:
                last_date = datetime.fromisoformat(last_active)
                days_ago = (datetime.now() - last_date).days
                
                # 如果 7 天内有过活跃，不归档
                if days_ago < 7:
                    return False
                
                # 30 天前活跃的，归档
                if days_ago > self.config["keep_active_days"]:
                    return True
            except Exception:
                pass
        
        # 默认不归档
        return False
    
    def archive_session(self, session_id: str, session_info: Dict) -> bool:
        """
        归档单个会话
        
        Args:
            session_id: 会话 ID
            session_info: 会话信息
            
        Returns:
            bool: 是否成功
        """
        try:
            # 创建归档目录 (按年月)
            month_dir = datetime.now().strftime("%Y-%m")
            target_dir = os.path.join(self.archive_path, month_dir)
            os.makedirs(target_dir, exist_ok=True)
            
            # 移动会话文件
            # 假设会话存储在 sessions/{session_id}.json
            source_file = os.path.join(self.base_path, "sessions", f"{session_id}.json")
            target_file = os.path.join(target_dir, f"{session_id}.json")
            
            if os.path.exists(source_file):
                shutil.move(source_file, target_file)
                
                # 压缩归档文件
                if self.config.get("compress_enabled", True):
                    compressed_file = self.compress_file(target_file)
                    if compressed_file:
                        os.remove(target_file)  # 删除原始文件
                        print(f"✓ 已归档并压缩: {session_id} -> {month_dir}/")
                    else:
                        print(f"✓ 已归档: {session_id} -> {month_dir}/")
                else:
                    print(f"✓ 已归档: {session_id} -> {month_dir}/")
                return True
            else:
                # 即使文件不存在，也记录归档信息
                info_file = os.path.join(target_dir, f"{session_id}_info.json")
                with open(info_file, 'w', encoding='utf-8') as f:
                    json.dump(session_info, f, ensure_ascii=False, indent=2)
                print(f"✓ 已归档(信息): {session_id} -> {month_dir}/")
                return True
                
        except Exception as e:
            print(f"✗ 归档失败 {session_id}: {e}")
            return False
    
    def compress_file(self, file_path: str) -> str:
        """
        压缩单个文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: 压缩文件路径，失败返回空字符串
        """
        compressed_path = file_path + ".gz"
        try:
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    f_out.write(f_in.read())
            return compressed_path
        except Exception as e:
            print(f"压缩失败 {file_path}: {e}")
            return ""
    
    def decompress_file(self, compressed_path: str, output_path: str = None) -> str:
        """
        解压文件
        
        Args:
            compressed_path: 压缩文件路径
            output_path: 输出路径（可选）
            
        Returns:
            str: 解压后的文件路径
        """
        if output_path is None:
            output_path = compressed_path.replace('.gz', '')
        
        try:
            with gzip.open(compressed_path, 'rb') as f_in:
                with open(output_path, 'wb') as f_out:
                    f_out.write(f_in.read())
            return output_path
        except Exception as e:
            print(f"解压失败 {compressed_path}: {e}")
            return ""
    
    def read_compressed_session(self, session_id: str) -> Optional[Dict]:
        """
        读取压缩的会话文件
        
        Args:
            session_id: 会话 ID
            
        Returns:
            Dict: 会话信息 或 None
        """
        # 查找压缩文件
        for root, dirs, files in os.walk(self.archive_path):
            for file in files:
                if file == f"{session_id}.json.gz":
                    compressed_path = os.path.join(root, file)
                    decompressed_path = self.decompress_file(compressed_path)
                    if decompressed_path:
                        try:
                            with open(decompressed_path, 'r', encoding='utf-8') as f:
                                return json.load(f)
                        except Exception:
                            pass
                    return None
                elif file == f"{session_id}.json":
                    # 未压缩的版本
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            return json.load(f)
                    except Exception:
                        pass
        return None
    
    def daily_flush(self, session_manager) -> Dict[str, Any]:
        """
        执行每日 Flush
        
        Args:
            session_manager: SessionManager 实例
            
        Returns:
            Dict: 执行统计
        """
        stats = {
            "total_sessions": 0,
            "archived": 0,
            "compressed": 0,
            "skipped": 0,
            "errors": 0,
            "timestamp": datetime.now().isoformat()
        }
        
        if not self.config["enabled"]:
            print("Flush 已禁用")
            return stats
        
        print(f"🔄 开始每日 Flush ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        
        # 获取所有会话
        sessions = session_manager.sessions
        stats["total_sessions"] = len(sessions)
        
        for session_id, info in sessions.items():
            try:
                info_dict = info.to_dict() if hasattr(info, 'to_dict') else info
                
                if self.should_archive(info_dict):
                    if self.archive_session(session_id, info_dict):
                        session_manager.archive_session(session_id)
                        stats["archived"] += 1
                        stats["compressed"] += 1  # 压缩计数
                    else:
                        stats["errors"] += 1
                else:
                    stats["skipped"] += 1
                    
            except Exception as e:
                print(f"✗ 处理会话失败 {session_id}: {e}")
                stats["errors"] += 1
        
        # 清理旧归档
        self.clean_old_archives()
        
        print(f"✓ Flush 完成: 归档 {stats['archived']}, 压缩 {stats['compressed']}, 跳过 {stats['skipped']}")
        
        return stats
    
    def clean_old_archives(self):
        """清理旧归档文件"""
        if not self.config.get("keep_archived_days"):
            return
        
        cutoff_date = datetime.now() - timedelta(days=self.config["keep_archived_days"])
        
        for root, dirs, files in os.walk(self.archive_path):
            for file in files:
                if file.endswith("_info.json"):
                    try:
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            info = json.load(f)
                        
                        last_active = info.get("last_active", "")
                        if last_active:
                            last_date = datetime.fromisoformat(last_active)
                            if last_date < cutoff_date:
                                os.remove(file_path)
                                print(f"🗑️ 已清理旧归档: {file}")
                    except Exception:
                        pass
    
    def get_archive_stats(self) -> Dict[str, Any]:
        """获取归档统计"""
        stats = {
            "total_archives": 0,
            "compressed_count": 0,
            "by_month": {}
        }
        
        if not os.path.exists(self.archive_path):
            return stats
        
        for item in os.listdir(self.archive_path):
            item_path = os.path.join(self.archive_path, item)
            if os.path.isdir(item_path):
                files = os.listdir(item_path)
                json_count = len([f for f in files if f.endswith(".json")])
                gz_count = len([f for f in files if f.endswith(".json.gz")])
                stats["by_month"][item] = {
                    "total": json_count + gz_count,
                    "compressed": gz_count
                }
                stats["total_archives"] += json_count + gz_count
                stats["compressed_count"] += gz_count
        
        return stats
    
    def manual_flush(self, session_manager, dry_run: bool = True) -> Dict[str, Any]:
        """
        手动触发 Flush（用于测试）
        
        Args:
            session_manager: SessionManager 实例
            dry_run: True 则只预览，不实际执行
            
        Returns:
            Dict: 预览/执行统计
        """
        stats = {
            "dry_run": dry_run,
            "sessions_to_archive": [],
            "total_sessions": len(session_manager.sessions)
        }
        
        for session_id, info in session_manager.sessions.items():
            info_dict = info.to_dict() if hasattr(info, 'to_dict') else info
            
            if self.should_archive(info_dict):
                stats["sessions_to_archive"].append({
                    "session_id": session_id,
                    "topic": info.topic,
                    "last_active": info.last_active,
                    "chunks": info.chunk_count
                })
        
        if dry_run:
            print(f"🔍 Dry Run - 将归档 {len(stats['sessions_to_archive'])} 个会话:")
            for s in stats["sessions_to_archive"]:
                print(f"  - {s['session_id']}: {s['topic']} ({s['chunks']} chunks)")
        else:
            return self.daily_flush(session_manager)
        
        return stats


# 测试
if __name__ == "__main__":
    from session_manager import SessionManager
    
    # 创建测试会话
    manager = SessionManager()
    sid = manager.start_session("测试会话")
    manager.add_chunk(sid)
    
    # Flush 测试
    flush_mgr = FlushManager()
    
    # 预览
    result = flush_mgr.manual_flush(manager, dry_run=True)
    print(f"\n预览: {len(result['sessions_to_archive'])} 个会话待归档")
