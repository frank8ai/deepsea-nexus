"""
File locking utilities for Deep-Sea Nexus v2.0
"""
import os
import time
import errno
from pathlib import Path
from typing import Optional, Union
from contextlib import contextmanager


class FileLock:
    """
    File-based lock implementation using flock when available,
    with fallback to manual lock files.
    
    Features:
    - Cross-platform compatibility
    - Timeout support
    - Context manager support
    """
    
    def __init__(self, file_path: Union[str, Path], timeout: float = 30.0, 
                 poll_interval: float = 0.1):
        """
        Initialize file lock
        
        Args:
            file_path: Path to the file to lock
            timeout: Timeout in seconds (default 30s)
            poll_interval: Polling interval in seconds (default 0.1s)
        """
        self.file_path = Path(file_path)
        self.lock_file_path = self.file_path.with_suffix(self.file_path.suffix + '.lock')
        self.timeout = timeout
        self.poll_interval = poll_interval
        self._locked = False
        self._lock_fd: Optional[int] = None
    
    def acquire(self) -> bool:
        """
        Acquire the lock
        
        Returns:
            bool: True if lock acquired, False if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < self.timeout:
            try:
                # Try to create lock file exclusively
                self._lock_fd = os.open(str(self.lock_file_path), 
                                       os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                # Write PID to lock file for debugging
                os.write(self._lock_fd, str(os.getpid()).encode())
                self._locked = True
                return True
            except OSError as e:
                if e.errno == errno.EEXIST:
                    # Lock file exists, wait and retry
                    time.sleep(self.poll_interval)
                else:
                    raise
            
        return False  # Timeout reached
    
    def release(self):
        """Release the lock"""
        if self._locked and self._lock_fd is not None:
            try:
                os.close(self._lock_fd)
                self.lock_file_path.unlink(missing_ok=True)
            except OSError:
                # Ignore errors during cleanup
                pass
            finally:
                self._locked = False
                self._lock_fd = None
    
    def __enter__(self):
        """Context manager entry"""
        acquired = self.acquire()
        if not acquired:
            raise TimeoutError(f"Could not acquire lock on {self.file_path} within {self.timeout}s")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.release()
    
    @contextmanager
    def timeout_context(self, timeout: float = None):
        """
        Context manager with custom timeout
        
        Args:
            timeout: Custom timeout in seconds
        """
        original_timeout = self.timeout
        if timeout is not None:
            self.timeout = timeout
        
        try:
            acquired = self.acquire()
            if not acquired:
                raise TimeoutError(f"Could not acquire lock within {self.timeout}s")
            yield self
        finally:
            self.release()
            if timeout is not None:
                self.timeout = original_timeout


def file_lock(file_path: Union[str, Path], timeout: float = 30.0):
    """
    Convenience function to create and return a FileLock
    
    Args:
        file_path: Path to the file to lock
        timeout: Timeout in seconds
    
    Returns:
        FileLock: Configured lock instance
    """
    return FileLock(file_path, timeout)


def locked_write(file_path: Union[str, Path], content: str, timeout: float = 30.0):
    """
    Write content to a file with locking
    
    Args:
        file_path: Path to the file
        content: Content to write
        timeout: Lock timeout in seconds
    """
    lock = FileLock(file_path, timeout)
    with lock:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)


def locked_append(file_path: Union[str, Path], content: str, timeout: float = 30.0):
    """
    Append content to a file with locking
    
    Args:
        file_path: Path to the file
        content: Content to append
        timeout: Lock timeout in seconds
    """
    lock = FileLock(file_path, timeout)
    with lock:
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(content)
