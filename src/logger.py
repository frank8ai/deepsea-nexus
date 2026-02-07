"""
日志系统模块
"""
import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional


class NexusLogger:
    """
    Nexus 日志管理器
    
    功能：
    - 配置日志级别
    - 控制台输出
    - 文件轮转
    """
    
    _instance: Optional['NexusLogger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_logger()
        return cls._instance
    
    def _init_logger(self):
        """初始化日志器"""
        self._logger = logging.getLogger("DeepSeaNexus")
        self._logger.setLevel(logging.INFO)
        
        # 清除现有处理器
        self._logger.handlers.clear()
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(formatter)
        
        self._logger.addHandler(console_handler)
    
    def set_level(self, level: str):
        """设置日志级别"""
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        self._logger.setLevel(level_map.get(level, logging.INFO))
    
    def debug(self, message: str):
        """Debug 日志"""
        self._logger.debug(message)
    
    def info(self, message: str):
        """Info 日志"""
        self._logger.info(message)
    
    def warning(self, message: str):
        """Warning 日志"""
        self._logger.warning(message)
    
    def error(self, message: str):
        """Error 日志"""
        self._logger.error(message)
    
    def critical(self, message: str):
        """Critical 日志"""
        self._logger.critical(message)


# 全局日志实例
logger = NexusLogger()


def get_logger(name: str = "DeepSeaNexus") -> NexusLogger:
    """获取日志器"""
    return logger
