"""
文件锁模块
"""
import os
import time
import fcntl
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

from .exceptions import LockAcquisitionError, TimeoutError


class FileLock:
    """
    文件锁（基于 flock）
    
    功能：
    - 线程安全的文件锁
    - 超时检测
    - 上下文管理器支持
    """
    
    def __init__(self, lock_file: str, timeout: int = 30):
        """
        初始化文件锁
        
        Args:
            lock_file: 锁文件路径
            timeout: 超时时间（秒）
        """
        self.lock_file = Path(lock_file)
        self.timeout = timeout
        self._lock_fd = None
    
    def acquire(self, blocking: bool = True) -> bool:
        """
        获取锁
        
        Args:
            blocking: 是否阻塞
        
        Returns:
            bool: 是否获取成功
        """
        # 确保父目录存在
        self.lock_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 创建锁文件（如果不存在）
        self.lock_file.touch(exist_ok=True)
        
        # 打开文件
        self._lock_fd = open(self.lock_file, 'w')
        
        try:
            if blocking:
                fcntl.flock(self._lock_fd.fileno(), fcntl.LOCK_EX)
                return True
            else:
                # 非阻塞模式
                result = fcntl.flock(self._lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                return result == 0
        except BlockingIOError:
            return False
    
    def release(self):
        """释放锁"""
        if self._lock_fd:
            fcntl.flock(self._lock_fd.fileno(), fcntl.LOCK_UN)
            self._lock_fd.close()
            self._lock_fd = None
    
    def __enter__(self):
        """上下文管理器进入"""
        start_time = time.time()
        
        while True:
            if self.acquire(blocking=False):
                return self
            
            if time.time() - start_time > self.timeout:
                raise LockAcquisitionError(str(self.lock_file))
            
            time.sleep(0.1)
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.release()
        return False


@contextmanager
def file_lock(lock_file: str, timeout: int = 30):
    """
    文件锁上下文管理器
    
    Args:
        lock_file: 锁文件路径
        timeout: 超时时间
    
    Usage:
        with file_lock("/path/to/lock"):
            # 受保护的代码
            pass
    """
    lock = FileLock(lock_file, timeout)
    lock.acquire()
    try:
        yield lock
    finally:
        lock.release()
