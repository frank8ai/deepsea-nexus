"""
Custom exceptions for Deep-Sea Nexus v2.0
"""


class NexusException(Exception):
    """Base exception for Nexus"""
    pass


class SessionNotFoundError(NexusException):
    """Raised when a session is not found"""
    def __init__(self, session_id: str):
        self.session_id = session_id
        super().__init__(f"Session not found: {session_id}")


class IndexFileError(NexusException):
    """Raised when there's an error with index files"""
    def __init__(self, message: str, file_path: str = None):
        self.file_path = file_path
        super().__init__(f"Index file error: {message}" + (f" at {file_path}" if file_path else ""))


class StorageFullError(NexusException):
    """Raised when storage is full"""
    def __init__(self, message: str = "Storage is full"):
        super().__init__(message)


class TimeoutError(NexusException):
    """Raised when an operation times out"""
    def __init__(self, operation: str, timeout: float):
        self.operation = operation
        self.timeout = timeout
        super().__init__(f"Operation '{operation}' timed out after {timeout}s")


class ConfigurationError(NexusException):
    """Raised when there's a configuration error"""
    def __init__(self, message: str):
        super().__init__(f"Configuration error: {message}")
