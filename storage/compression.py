"""
Compression Backends - Unified Compression Implementation

Eliminates code duplication between nexus_core.py and flush_manager.py.
Supports: gzip, zstd, lz4
"""

import gzip
from pathlib import Path
from typing import Optional
import logging

from .base import CompressionBackend, StorageResult

logger = logging.getLogger(__name__)


class GzipBackend(CompressionBackend):
    """
    Gzip compression backend
    
    Standard compression, widely compatible.
    Compression ratio: Good
    Speed: Moderate
    """
    
    def __init__(self, level: int = 6):
        """
        Args:
            level: Compression level (1-9, default 6)
        """
        self.level = level
    
    @property
    def algorithm_name(self) -> str:
        return "gzip"
    
    @property
    def file_extension(self) -> str:
        return ".gz"
    
    def compress(self, data: bytes) -> bytes:
        return gzip.compress(data, compresslevel=self.level)
    
    def decompress(self, data: bytes) -> bytes:
        return gzip.decompress(data)


class ZstdBackend(CompressionBackend):
    """
    Zstandard compression backend
    
    Modern compression algorithm from Facebook.
    Compression ratio: Excellent
    Speed: Fast
    
    Requires: pip install zstandard
    """
    
    def __init__(self, level: int = 3):
        """
        Args:
            level: Compression level (1-22, default 3)
        """
        self.level = level
        self._zstd = None
        self._ensure_import()
    
    def _ensure_import(self):
        """Lazy import zstandard"""
        if self._zstd is None:
            try:
                import zstandard as zstd
                self._zstd = zstd
            except ImportError:
                raise ImportError(
                    "zstandard is required for ZstdBackend. "
                    "Install with: pip install zstandard"
                )
    
    @property
    def algorithm_name(self) -> str:
        return "zstd"
    
    @property
    def file_extension(self) -> str:
        return ".zst"
    
    def compress(self, data: bytes) -> bytes:
        self._ensure_import()
        cctx = self._zstd.ZstdCompressor(level=self.level)
        return cctx.compress(data)
    
    def decompress(self, data: bytes) -> bytes:
        self._ensure_import()
        dctx = self._zstd.ZstdDecompressor()
        return dctx.decompress(data)


class Lz4Backend(CompressionBackend):
    """
    LZ4 compression backend
    
    Extremely fast compression.
    Compression ratio: Moderate
    Speed: Very fast
    
    Requires: pip install lz4
    """
    
    def __init__(self):
        self._lz4 = None
        self._ensure_import()
    
    def _ensure_import(self):
        """Lazy import lz4"""
        if self._lz4 is None:
            try:
                import lz4.frame
                self._lz4 = lz4.frame
            except ImportError:
                raise ImportError(
                    "lz4 is required for Lz4Backend. "
                    "Install with: pip install lz4"
                )
    
    @property
    def algorithm_name(self) -> str:
        return "lz4"
    
    @property
    def file_extension(self) -> str:
        return ".lz4"
    
    def compress(self, data: bytes) -> bytes:
        self._ensure_import()
        return self._lz4.compress(data)
    
    def decompress(self, data: bytes) -> bytes:
        self._ensure_import()
        return self._lz4.decompress(data)


class CompressionManager:
    """
    Compression Manager - Unified interface for all compression operations
    
    This class eliminates code duplication between modules by providing
    a single, reusable compression interface.
    
    Usage:
        # In any module, instead of implementing compression:
        from storage.compression import CompressionManager
        
        cm = CompressionManager('gzip')
        cm.compress_file('data.txt')  # Creates data.txt.gz
        cm.decompress_file('data.txt.gz')  # Creates data.txt
    
    Backends:
        - gzip: Standard, compatible (default)
        - zstd: Better compression, faster (requires zstandard)
        - lz4: Fastest compression (requires lz4)
    """
    
    BACKENDS = {
        "gzip": GzipBackend,
        "zstd": ZstdBackend,
        "lz4": Lz4Backend,
    }
    
    def __init__(self, algorithm: str = "gzip", **kwargs):
        """
        Initialize compression manager
        
        Args:
            algorithm: Compression algorithm (gzip, zstd, lz4)
            **kwargs: Backend-specific options
        """
        if algorithm not in self.BACKENDS:
            available = ", ".join(self.available_algorithms())
            raise ValueError(f"Unknown algorithm: {algorithm}. Available: {available}")
        
        self.algorithm = algorithm
        self._backend = self.BACKENDS[algorithm](**kwargs)
    
    @property
    def backend(self) -> CompressionBackend:
        """Get underlying backend"""
        return self._backend
    
    def compress(self, data: bytes) -> bytes:
        """Compress bytes"""
        return self._backend.compress(data)
    
    def decompress(self, data: bytes) -> bytes:
        """Decompress bytes"""
        return self._backend.decompress(data)
    
    def compress_file(self, source: str, target: Optional[str] = None) -> StorageResult:
        """
        Compress a file
        
        Args:
            source: Source file path
            target: Target file path (optional, defaults to source + extension)
            
        Returns:
            StorageResult with target_path
        """
        return self._backend.compress_file(source, target)
    
    def decompress_file(self, source: str, target: Optional[str] = None) -> StorageResult:
        """
        Decompress a file
        
        Args:
            source: Compressed file path
            target: Target file path (optional)
            
        Returns:
            StorageResult with target_path
        """
        return self._backend.decompress_file(source, target)
    
    def read_compressed(self, path: str, encoding: str = 'utf-8') -> StorageResult:
        """
        Read a potentially compressed file
        
        Automatically detects compression by extension and decompresses if needed.
        
        Args:
            path: File path
            encoding: Text encoding
            
        Returns:
            StorageResult with content string
        """
        try:
            path_obj = Path(path)
            
            if not path_obj.exists():
                return StorageResult.err(f"File not found: {path}")
            
            data = path_obj.read_bytes()
            
            # Detect compression by extension
            if path_obj.suffix == '.gz':
                data = gzip.decompress(data)
            elif path_obj.suffix == '.zst':
                import zstandard
                data = zstandard.ZstdDecompressor().decompress(data)
            elif path_obj.suffix == '.lz4':
                import lz4.frame
                data = lz4.frame.decompress(data)
            
            return StorageResult.ok(data.decode(encoding))
            
        except Exception as e:
            return StorageResult.err(str(e))
    
    @classmethod
    def available_algorithms(cls) -> list:
        """Get list of available algorithms"""
        available = ["gzip"]  # Always available
        
        # Check optional dependencies
        try:
            import zstandard
            available.append("zstd")
        except ImportError:
            pass
        
        try:
            import lz4.frame
            available.append("lz4")
        except ImportError:
            pass
        
        return available
    
    @classmethod
    def benchmark(cls, data: bytes, algorithms: Optional[list] = None) -> dict:
        """
        Benchmark compression algorithms
        
        Args:
            data: Data to compress
            algorithms: List of algorithms to test (default: all available)
            
        Returns:
            Dict with compression ratio and speed for each algorithm
        """
        import time
        
        if algorithms is None:
            algorithms = cls.available_algorithms()
        
        results = {}
        
        for algo in algorithms:
            try:
                cm = cls(algo)
                
                # Compression
                start = time.time()
                compressed = cm.compress(data)
                compress_time = time.time() - start
                
                # Decompression
                start = time.time()
                decompressed = cm.decompress(compressed)
                decompress_time = time.time() - start
                
                # Verify
                assert decompressed == data, f"Data mismatch for {algo}"
                
                results[algo] = {
                    "original_size": len(data),
                    "compressed_size": len(compressed),
                    "ratio": len(compressed) / len(data),
                    "compress_time_ms": compress_time * 1000,
                    "decompress_time_ms": decompress_time * 1000,
                }
                
            except Exception as e:
                results[algo] = {"error": str(e)}
        
        return results


# Convenience functions for backward compatibility
def compress_file(source: str, target: Optional[str] = None, 
                  algorithm: str = "gzip") -> StorageResult:
    """
    Convenience function to compress a file
    
    Replaces duplicate implementations in nexus_core.py and flush_manager.py
    """
    cm = CompressionManager(algorithm)
    return cm.compress_file(source, target)


def decompress_file(source: str, target: Optional[str] = None,
                    algorithm: str = "gzip") -> StorageResult:
    """
    Convenience function to decompress a file
    
    Replaces duplicate implementations in nexus_core.py and flush_manager.py
    """
    cm = CompressionManager(algorithm)
    return cm.decompress_file(source, target)


def read_compressed(path: str, encoding: str = 'utf-8') -> StorageResult:
    """
    Convenience function to read a compressed file
    
    Replaces duplicate implementations in nexus_core.py and flush_manager.py
    """
    cm = CompressionManager("gzip")  # Algorithm auto-detected
    return cm.read_compressed(path, encoding)
