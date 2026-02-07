"""
Logging system for Deep-Sea Nexus v2.0
"""
import logging
import sys
from pathlib import Path
from typing import Optional


class NexusLogger:
    """
    Nexus Logger
    
    Features:
    - Configurable log levels
    - Console output
    - File output (optional)
    - Structured logging
    """
    
    _instance: Optional['NexusLogger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup_logger()
        return cls._instance
    
    def _setup_logger(self):
        """Setup the logger"""
        self._logger = logging.getLogger('DeepSeaNexus')
        
        # Prevent adding handlers multiple times
        if self._logger.handlers:
            return
            
        # Set default level
        self._logger.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
        
        # Clear any default handlers to prevent duplicates
        self._logger.propagate = False
    
    def set_level(self, level: int):
        """Set logging level"""
        if self._logger:
            self._logger.setLevel(level)
    
    def add_file_handler(self, file_path: str, level: int = logging.DEBUG):
        """Add file handler"""
        if self._logger:
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                file_path, 
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(level)
            self._logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """Debug level log"""
        if self._logger:
            self._logger.debug(message)
    
    def info(self, message: str):
        """Info level log"""
        if self._logger:
            self._logger.info(message)
    
    def warning(self, message: str):
        """Warning level log"""
        if self._logger:
            self._logger.warning(message)
    
    def error(self, message: str):
        """Error level log"""
        if self._logger:
            self._logger.error(message)
    
    def critical(self, message: str):
        """Critical level log"""
        if self._logger:
            self._logger.critical(message)


# Global logger instance
logger = NexusLogger()
