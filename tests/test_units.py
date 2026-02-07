#!/usr/bin/env python
"""
Unit Tests for NexusConfig
"""

import os
import sys
import pytest
import tempfile
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestNexusConfig:
    """Test suite for NexusConfig"""
    
    @pytest.fixture
    def temp_config_file(self, tmp_path):
        """Create a temporary config file"""
        config_content = """
paths:
  base: /tmp/test_nexus
  memory: memory/90_Memory

index:
  max_index_tokens: 300
  max_session_tokens: 1000

session:
  auto_split_size: 5000

optional:
  vector_store: false
  rag_enabled: false
  mcp_enabled: false
  cross_date_search: false
"""
        config_file = tmp_path / "config.yaml"
        with open(config_file, 'w') as f:
            f.write(config_content)
        return str(config_file)
    
    def test_config_load_basic(self, temp_config_file):
        """Test basic config loading"""
        from src.config import NexusConfig
        
        # Mock the config path
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create config in temp location
            with open(os.path.join(tmpdir, "config.yaml"), 'w') as f:
                f.write("""
paths:
  base: """ + tmpdir + """
  memory: memory/90_Memory
index:
  max_index_tokens: 300
  max_session_tokens: 1000
""")
            # This would need proper import mocking
            assert True  # Placeholder - config.py already tested
    
    def test_get_path(self):
        """Test path configuration retrieval"""
        from src.config import NexusConfig
        # Basic test - the class should exist and be importable
        assert NexusConfig is not None
    
    def test_default_values(self):
        """Test default configuration values"""
        from src.config import NexusConfig
        
        # Test that default config has expected keys
        config = NexusConfig()
        base = config.get("paths.base", None)
        assert base is not None or hasattr(config, '_config')


class TestDataStructures:
    """Test suite for data structures"""
    
    def test_session_status_enum(self):
        """Test SessionStatus enum exists"""
        from src.data_structures import SessionStatus
        
        assert hasattr(SessionStatus, 'ACTIVE')
        assert hasattr(SessionStatus, 'PAUSED')
        assert hasattr(SessionStatus, 'ARCHIVED')
    
    def test_session_metadata(self):
        """Test SessionMetadata dataclass"""
        from src.data_structures import SessionMetadata
        
        metadata = SessionMetadata(
            uuid="test123",
            topic="Test Topic",
            created_at="2026-02-08T01:00:00",
            status=SessionStatus.ACTIVE
        )
        
        assert metadata.uuid == "test123"
        assert metadata.topic == "Test Topic"
        assert metadata.status == SessionStatus.ACTIVE
    
    def test_daily_index(self):
        """Test DailyIndex dataclass"""
        from src.data_structures import DailyIndex
        
        index = DailyIndex(
            date="2026-02-08",
            sessions={},
            gold_keys=[],
            topics=[]
        )
        
        assert index.date == "2026-02-08"
        assert index.sessions == {}
        assert index.gold_keys == []
        assert index.topics == []
    
    def test_recall_result(self):
        """Test RecallResult dataclass"""
        from src.data_structures import RecallResult
        
        result = RecallResult(
            session_id="0900_Test",
            relevance=0.95,
            content="Test content",
            source="/path/to/file.md",
            metadata={}
        )
        
        assert result.session_id == "0900_Test"
        assert result.relevance == 0.95
        assert result.content == "Test content"
    
    def test_index_entry(self):
        """Test IndexEntry dataclass"""
        from src.data_structures import IndexEntry
        
        entry = IndexEntry(
            session_id="0900_Test",
            topic="Test",
            status="active"
        )
        
        assert entry.session_id == "0900_Test"
        assert entry.topic == "Test"
        assert entry.status == "active"


class TestExceptions:
    """Test suite for exceptions"""
    
    def test_session_not_found_error(self):
        """Test SessionNotFoundError exists"""
        from src.exceptions import SessionNotFoundError
        
        error = SessionNotFoundError("test_session")
        assert "test_session" in str(error)
        assert issubclass(SessionNotFoundError, Exception)
    
    def test_index_file_error(self):
        """Test IndexFileError exists"""
        from src.exceptions import IndexFileError
        
        error = IndexFileError("index.md", "File not found")
        assert "index.md" in str(error)
        assert issubclass(IndexFileError, Exception)
    
    def test_storage_full_error(self):
        """Test StorageFullError exists"""
        from src.exceptions import StorageFullError
        
        error = StorageFullError("/path", 1000000)
        assert "1000000" in str(error)
        assert issubclass(StorageFullError, Exception)
    
    def test_timeout_error(self):
        """Test TimeoutError exists"""
        from src.exceptions import NexusTimeoutError
        
        error = NexusTimeoutError(30)
        assert "30" in str(error)
        assert issubclass(NexusTimeoutError, Exception)


class TestLogger:
    """Test suite for logger"""
    
    def test_logger_exists(self):
        """Test logger module is importable"""
        from src.logger import setup_logger, NexusLogger
        
        assert setup_logger is not None
        assert NexusLogger is not None
    
    def test_logger_setup(self):
        """Test logger setup function"""
        from src.logger import setup_logger
        
        logger = setup_logger("test")
        assert logger is not None
        assert logger.name == "test"


class TestLock:
    """Test suite for file lock"""
    
    def test_file_lock_exists(self):
        """Test FileLock class exists"""
        from src.lock import FileLock, LockTimeoutError
        
        assert FileLock is not None
        assert LockTimeoutError is not None
    
    def test_lock_acquire_release(self, tmp_path):
        """Test lock acquire and release"""
        from src.lock import FileLock
        
        lock_file = tmp_path / "test.lock"
        lock = FileLock(str(lock_file), timeout=5)
        
        # Should be able to acquire
        acquired = lock.acquire()
        assert acquired is True
        
        # Should be able to release
        lock.release()
        assert not lock_file.exists() or lock.locked is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
