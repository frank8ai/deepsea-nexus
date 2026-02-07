"""
异常定义模块
"""


class NexusException(Exception):
    """Nexus 基础异常"""
    pass


class SessionNotFoundError(NexusException):
    """Session 未找到异常"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        super().__init__(f"Session 未找到: {session_id}")


class IndexFileError(NexusException):
    """索引文件异常"""
    
    def __init__(self, message: str):
        super().__init__(f"索引文件错误: {message}")


class StorageFullError(NexusException):
    """存储空间不足异常"""
    
    def __init__(self, path: str):
        self.path = path
        super().__init__(f"存储空间不足: {path}")


class TimeoutError(NexusException):
    """操作超时异常"""
    
    def __init__(self, operation: str, timeout: int):
        self.operation = operation
        self.timeout = timeout
        super().__init__(f"操作超时: {operation} (超时 {timeout} 秒)")


class LockAcquisitionError(NexusException):
    """获取文件锁失败异常"""
    
    def __init__(self, path: str):
        self.path = path
        super().__init__(f"无法获取文件锁: {path}")


class ConfigurationError(NexusException):
    """配置错误异常"""
    
    def __init__(self, key: str):
        super().__init__(f"配置错误: {key}")


class MigrationError(NexusException):
    """迁移错误异常"""
    
    def __init__(self, message: str):
        super().__init__(f"迁移错误: {message}")
