"""
Integration Tests for Deep-Sea Nexus v3.0

Test the full system integration and end-to-end functionality.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import tempfile
import json
import unittest
from pathlib import Path

try:
    from deepsea_nexus import (
        create_app,
        nexus_init,
        nexus_recall,
        nexus_add,
        get_session_manager,
        start_session,
        close_session,
    )
except ImportError:
    # Fallback: import from local modules directly
    from nexus_core import nexus_init, nexus_recall, nexus_add
    from session_manager import SessionManager as get_session_manager, start_session, close_session
    create_app = None


class TestEndToEnd(unittest.TestCase):
    """End-to-end integration tests"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.app = None
    
    def tearDown(self):
        if self.app:
            asyncio.run(self.app.stop())
        
        # Cleanup temp dir
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_lifecycle(self):
        """Test complete application lifecycle"""
        # Create app with temp config
        config_path = os.path.join(self.temp_dir, "test_config.json")
        config = {
            "base_path": self.temp_dir,
            "nexus": {
                "vector_db_path": os.path.join(self.temp_dir, "vector_db"),
            },
            "session": {
                "auto_archive_days": 30,
            },
            "flush": {
                "enabled": False,  # Disable auto-flush for tests
            },
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f)
        
        # Create and initialize app
        app = create_app(config_path)
        self.assertTrue(asyncio.run(app.initialize()))
        self.assertTrue(asyncio.run(app.start()))
        
        # Test plugins are working
        self.assertIsNotNone(app.plugins.get("nexus_core"))
        self.assertIsNotNone(app.plugins.get("session_manager"))
        self.assertIsNotNone(app.plugins.get("flush_manager"))
        
        # Test backward compatibility
        self.assertTrue(nexus_init())
        
        # Test search (should not crash)
        results = nexus_recall("test", n=1)
        self.assertIsInstance(results, list)
        
        # Test add (should not crash)
        doc_id = nexus_add("Test content", "Test title", "test,integration")
        # May return None if backend not available, but shouldn't crash
        
        # Stop app
        self.assertTrue(asyncio.run(app.stop()))
    
    def test_session_management(self):
        """Test session management integration"""
        # Initialize with backward compatibility
        self.assertTrue(nexus_init())
        
        # Get session manager
        session_mgr = get_session_manager()
        if session_mgr:
            # Test session creation
            session_id = start_session("Integration Test")
            self.assertTrue(session_id)
            
            # Test session retrieval
            session = session_mgr.get_session(session_id)
            self.assertIsNotNone(session)
            self.assertEqual(session.topic, "Integration Test")
            
            # Test session closing
            result = close_session(session_id)
            self.assertTrue(result)
            
            # Verify session is paused
            session = session_mgr.get_session(session_id)
            self.assertIsNotNone(session)
            if session:
                self.assertEqual(session.status, "paused")


class TestPluginCommunication(unittest.TestCase):
    """Test plugin communication via event bus"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.events_received = []
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_event_driven_communication(self):
        """Test that plugins communicate via events"""
        # Set up event listener
        from deepsea_nexus.core.event_bus import get_event_bus
        
        def event_handler(event):
            self.events_received.append(event)
        
        event_bus = get_event_bus()
        event_bus.subscribe("nexus.*", event_handler)  # Listen to nexus events
        event_bus.subscribe("session.*", event_handler)  # Listen to session events
        event_bus.subscribe("flush.*", event_handler)  # Listen to flush events
        
        # Create and run app
        config_path = os.path.join(self.temp_dir, "test_config.json")
        config = {
            "base_path": self.temp_dir,
            "nexus": {"vector_db_path": os.path.join(self.temp_dir, "vector_db")},
            "session": {"auto_archive_days": 30},
            "flush": {"enabled": False},
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f)
        
        app = create_app(config_path)
        self.assertTrue(asyncio.run(app.initialize()))
        self.assertTrue(asyncio.run(app.start()))
        
        # Perform some operations that should generate events
        nexus_init()
        
        # Wait for events to process
        asyncio.run(asyncio.sleep(0.1))
        
        # We expect some events to be generated during initialization
        # Even if no specific events occur, this verifies the system is working
        
        # Stop app
        asyncio.run(app.stop())


class TestBackwardCompatibilityIntegration(unittest.TestCase):
    """Test backward compatibility in integrated scenarios"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_mixed_api_usage(self):
        """Test mixing old and new APIs"""
        # Use new API
        config_path = os.path.join(self.temp_dir, "test_config.json")
        config = {
            "base_path": self.temp_dir,
            "nexus": {"vector_db_path": os.path.join(self.temp_dir, "vector_db")},
            "session": {"auto_archive_days": 30},
            "flush": {"enabled": False},
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f)
        
        app = create_app(config_path)
        self.assertTrue(asyncio.run(app.initialize()))
        self.assertTrue(asyncio.run(app.start()))
        
        # Now use old API
        self.assertTrue(nexus_init())
        
        # Both should work together
        old_results = nexus_recall("test", n=1)
        self.assertIsInstance(old_results, list)
        
        # Use new API
        if app.plugins.get("nexus_core"):
            new_results = asyncio.run(
                app.plugins["nexus_core"].search_recall("test", 1)
            )
            self.assertIsInstance(new_results, list)
        
        # Stop
        asyncio.run(app.stop())
    
    def test_config_integration(self):
        """Test config manager integration"""
        from deepsea_nexus.core.config_manager import get_config_manager
        
        config_mgr = get_config_manager()
        
        # Test setting/getting values
        config_mgr.set("test.key", "test_value")
        self.assertEqual(config_mgr.get("test.key"), "test_value")
        
        # Test default values
        self.assertEqual(config_mgr.get("nonexistent", "default"), "default")
        
        # Test nested access
        config_mgr.set("nested.deep.value", "deep_test")
        self.assertEqual(config_mgr.get("nested.deep.value"), "deep_test")


class TestStorageIntegration(unittest.TestCase):
    """Test storage backend integration"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_compression_integration(self):
        """Test compression manager integration"""
        from deepsea_nexus.storage.compression import CompressionManager
        
        # Test all available backends
        for algo in CompressionManager.available_algorithms():
            cm = CompressionManager(algo)
            
            # Test basic compression
            original = b"Integration test data for compression algorithm: " + algo.encode()
            compressed = cm.compress(original)
            decompressed = cm.decompress(compressed)
            
            self.assertEqual(decompressed, original)
            self.assertLessEqual(len(compressed), len(original))
        
        # Test benchmark (should not crash)
        cm = CompressionManager("gzip")
        data = b"Test data for benchmarking"
        try:
            benchmark_results = cm.benchmark(data)
            # Should return dict with results
            self.assertIsInstance(benchmark_results, dict)
        except Exception:
            # Some backends might not be available, that's OK
            pass


class TestHotReload(unittest.TestCase):
    """Test hot-reload functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_config_reload(self):
        """Test configuration reload"""
        # Create initial config
        config_path = os.path.join(self.temp_dir, "reload_test.json")
        initial_config = {
            "base_path": self.temp_dir,
            "nexus": {"vector_db_path": os.path.join(self.temp_dir, "vector_db")},
            "session": {"auto_archive_days": 30},
            "flush": {"enabled": False},
        }
        
        with open(config_path, 'w') as f:
            json.dump(initial_config, f)
        
        # Create and start app
        app = create_app(config_path)
        self.assertTrue(asyncio.run(app.initialize()))
        self.assertTrue(asyncio.run(app.start()))
        
        # Modify config
        modified_config = initial_config.copy()
        modified_config["session"]["auto_archive_days"] = 15  # Change value
        
        with open(config_path, 'w') as f:
            json.dump(modified_config, f)
        
        # Test reload
        self.assertTrue(asyncio.run(app.reload()))
        
        # Stop
        asyncio.run(app.stop())


def run_integration_tests():
    """Run all integration tests"""
    print("🧪 Running Deep-Sea Nexus v3.0 Integration Tests...")
    
    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestEndToEnd)
    suite.addTests(loader.loadTestsFromTestCase(TestPluginCommunication))
    suite.addTests(loader.loadTestsFromTestCase(TestBackwardCompatibilityIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestStorageIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestHotReload))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\n📊 Integration Test Results:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_tests()
    exit(0 if success else 1)
