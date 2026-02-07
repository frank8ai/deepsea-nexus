"""
Phase 1 验收测试：基础设施
"""
import pytest
from pathlib import Path
import sys

# 添加 src 目录
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import NexusConfig
from src.data_structures import (
    SessionMetadata, SessionStatus, Session,
    DailyIndex, RecallResult, NexusConfig as DS_Config
)


class TestProjectStructure:
    """项目结构测试"""
    
    @property
    def base_path(self):
        """获取正确的基础路径"""
        # Deep-Sea Nexus v2.0 存储在 OpenClaw workspace
        return Path.home() / ".openclaw" / "workspace" / "DEEP_SEA_NEXUS_V2"
    
    def test_directories_exist(self):
        """所有目录存在"""
        base = self.base_path
        required = [
            "src",
            "src/chunking",
            "src/embedding",
            "src/vector_store",
            "src/retrieval",
            "src/rag",
            "scripts",
            "tests",
            "memory/90_Memory",
            "memory/00_Inbox",
            "memory/10_Projects"
        ]
        for d in required:
            assert (base / d).exists(), f"Missing: {base / d}"
    
    def test_config_exists(self):
        """配置文件存在"""
        base = self.base_path
        assert (base / "config.yaml").exists()
    
    def test_readme_exists(self):
        """README 存在"""
        base = self.base_path
        assert (base / "README.md").exists()
    
    def test_gitignore_exists(self):
        """gitignore 存在"""
        base = self.base_path
        assert (base / ".gitignore").exists()


class TestConfig:
    """配置测试"""
    
    @property
    def base_path(self):
        return Path.home() / ".openclaw" / "workspace" / "DEEP_SEA_NEXUS_V2"
    
    def test_config_load(self):
        """测试配置加载"""
        config = NexusConfig()
        assert config.get("project.name") == "Deep-Sea Nexus v2.0"
    
    def test_config_paths(self):
        """测试路径配置"""
        config = NexusConfig()
        assert config.base_path.exists()
        assert config.memory_path.exists()
    
    def test_config_values(self):
        """测试配置值"""
        config = NexusConfig()
        assert config.max_index_tokens == 300
        assert config.max_session_tokens == 1000


class TestDataStructures:
    """数据结构测试"""
    
    def test_session_status(self):
        """测试 Session 状态枚举"""
        assert SessionStatus.ACTIVE.value == "active"
        assert SessionStatus.PAUSED.value == "paused"
        assert SessionStatus.ARCHIVED.value == "archived"
    
    def test_session_metadata(self):
        """测试 Session 元数据"""
        meta = SessionMetadata(
            uuid="test-001",
            topic="Test",
            created_at="2026-02-07T10:00:00",
            last_active="2026-02-07T10:00:00"
        )
        
        assert meta.uuid == "test-001"
        assert meta.topic == "Test"
        assert meta.status == SessionStatus.ACTIVE
        assert meta.gold_count == 0
        assert meta.word_count == 0
    
    def test_recall_result(self):
        """测试召回结果"""
        result = RecallResult(
            session_id="0923_Test",
            relevance=0.95,
            content="测试内容",
            source="memory/session.md"
        )
        
        assert result.session_id == "0923_Test"
        assert result.relevance == 0.95
        assert "测试" in result.content
    
    def test_daily_index(self):
        """测试每日索引"""
        index = DailyIndex(
            date="2026-02-07",
            sessions={},
            gold_keys=["ChromaDB"],
            topics=["Python"],
            paused_sessions={}
        )
        
        assert index.date == "2026-02-07"
        assert "ChromaDB" in index.gold_keys
        assert "Python" in index.topics


class TestExceptions:
    """异常测试"""
    
    def test_session_not_found(self):
        """测试 Session 未找到异常"""
        from src.exceptions import SessionNotFoundError
        
        exc = SessionNotFoundError("test-session")
        assert "test-session" in str(exc)
    
    def test_index_file_error(self):
        """测试索引文件异常"""
        from src.exceptions import IndexFileError
        
        exc = IndexFileError("Invalid format")
        assert "Invalid format" in str(exc)
    
    def test_timeout_error(self):
        """测试超时异常"""
        from src.exceptions import TimeoutError
        
        exc = TimeoutError("write", 30)
        assert "write" in str(exc)


class TestLogger:
    """日志测试"""
    
    def test_logger_creation(self):
        """测试日志器创建"""
        from src.logger import NexusLogger, get_logger
        
        logger = get_logger()
        assert logger is not None
    
    def test_logger_levels(self):
        """测试日志级别"""
        from src.logger import logger
        
        # 验证不抛出异常
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")


class TestFileLock:
    """文件锁测试"""
    
    def test_lock_creation(self):
        """测试锁创建"""
        from src.lock import FileLock
        
        lock = FileLock("/tmp/test_lock", timeout=5)
        assert lock.timeout == 5
    
    def test_lock_acquire_release(self):
        """测试锁获取和释放"""
        from src.lock import FileLock
        
        import tempfile
        with tempfile.NamedTemporaryFile() as f:
            lock = FileLock(f.name, timeout=5)
            
            # 获取锁 (使用阻塞模式)
            acquired = lock.acquire(blocking=True)
            assert acquired is True
            
            # 释放锁
            lock.release()
    
    def test_lock_context_manager(self):
        """测试上下文管理器"""
        from src.lock import file_lock
        
        import tempfile
        with tempfile.NamedTemporaryFile() as f:
            with file_lock(f.name, timeout=5) as lock:
                assert lock is not None


# 验收测试
def test_phase1_completion():
    """Phase 1 完成检查"""
    base = Path.home() / ".openclaw" / "workspace" / "DEEP_SEA_NEXUS_V2"
    
    # 必须存在的文件
    required_files = [
        "config.yaml",
        "README.md",
        "requirements.txt",
        ".gitignore",
        "src/config.py",
        "src/data_structures.py",
        "src/exceptions.py",
        "src/logger.py",
        "src/lock.py",
        "tests/conftest.py"
    ]
    
    for f in required_files:
        assert (base / f).exists(), f"Missing: {base / f}"
    
    # 验证配置
    config = NexusConfig()
    assert config.get("project.name") == "Deep-Sea Nexus v2.0"
    assert config.max_index_tokens == 300
    
    print("✅ Phase 1 验收通过")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
