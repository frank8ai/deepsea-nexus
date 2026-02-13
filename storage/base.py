"""
Storage Abstraction Layer

Provides unified interfaces for different storage backends.
Allows hot-swapping of storage implementations without affecting business logic.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class StorageBackendType(Enum):
    """Storage backend types"""
    VECTOR = "vector"
    SESSION = "session"
    COMPRESSION = "compression"


@dataclass
class StorageResult:
    """Generic storage operation result"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    backend: Optional[str] = None
    
    @property
    def is_ok(self) -> bool:
        return self.success
    
    @classmethod
    def ok(cls, data: Any = None, backend: str = None) -> "StorageResult":
        return cls(success=True, data=data, backend=backend)
    
    @classmethod
    def err(cls, error: str, backend: str = None) -> "StorageResult":
        return cls(success=False, error=error, backend=backend)


@dataclass
class RecallResult:
    """Semantic search result"""
    content: str
    source: str
    relevance: float
    metadata: Optional[Dict[str, Any]] = None
    doc_id: Optional[str] = None


class VectorStorageBackend(ABC):
    """
    Abstract base class for vector storage backends
    
    Implementations: ChromaDB, FAISS, Milvus, Pinecone, etc.
    """
    
    @property
    @abstractmethod
    def backend_name(self) -> str:
        """Backend identifier"""
        pass
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the storage backend
        
        Args:
            config: Backend-specific configuration
            
        Returns:
            bool: True if initialized successfully
        """
        pass
    
    @abstractmethod
    async def add(self, content: str, 
                  metadata: Optional[Dict[str, Any]] = None,
                  doc_id: Optional[str] = None) -> StorageResult:
        """
        Add a document to the vector store
        
        Args:
            content: Document content
            metadata: Optional metadata
            doc_id: Optional document ID
            
        Returns:
            StorageResult with doc_id on success
        """
        pass
    
    @abstractmethod
    async def add_batch(self, documents: List[Tuple[str, Dict[str, Any]]]) -> StorageResult:
        """
        Add multiple documents in batch
        
        Args:
            documents: List of (content, metadata) tuples
            
        Returns:
            StorageResult with list of doc_ids on success
        """
        pass
    
    @abstractmethod
    async def search(self, query: str, 
                     limit: int = 5,
                     filters: Optional[Dict[str, Any]] = None,
                     min_relevance: float = 0.0) -> StorageResult:
        """
        Semantic search
        
        Args:
            query: Search query
            limit: Maximum results
            filters: Optional metadata filters
            min_relevance: Minimum relevance score
            
        Returns:
            StorageResult with List[RecallResult] on success
        """
        pass
    
    @abstractmethod
    async def get(self, doc_id: str) -> StorageResult:
        """
        Get a document by ID
        
        Args:
            doc_id: Document ID
            
        Returns:
            StorageResult with document data
        """
        pass
    
    @abstractmethod
    async def delete(self, doc_id: str) -> StorageResult:
        """
        Delete a document
        
        Args:
            doc_id: Document ID
            
        Returns:
            StorageResult
        """
        pass
    
    @abstractmethod
    async def update(self, doc_id: str, 
                     content: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> StorageResult:
        """
        Update a document
        
        Args:
            doc_id: Document ID
            content: New content (optional)
            metadata: New metadata (merged if provided)
            
        Returns:
            StorageResult
        """
        pass
    
    @abstractmethod
    async def count(self) -> StorageResult:
        """
        Get document count
        
        Returns:
            StorageResult with count
        """
        pass
    
    @abstractmethod
    async def get_stats(self) -> StorageResult:
        """
        Get backend statistics
        
        Returns:
            StorageResult with stats dict
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> StorageResult:
        """
        Check backend health
        
        Returns:
            StorageResult with health status
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close backend connection"""
        pass
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class SessionStorageBackend(ABC):
    """
    Abstract base class for session storage backends
    
    Implementations: JSON file, SQLite, Redis, etc.
    """
    
    @property
    @abstractmethod
    def backend_name(self) -> str:
        """Backend identifier"""
        pass
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the storage backend"""
        pass
    
    @abstractmethod
    async def save_session(self, session_id: str,
                           data: Dict[str, Any]) -> StorageResult:
        """
        Save session data
        
        Args:
            session_id: Session identifier
            data: Session data
            
        Returns:
            StorageResult
        """
        pass
    
    @abstractmethod
    async def load_session(self, session_id: str) -> StorageResult:
        """
        Load session data
        
        Args:
            session_id: Session identifier
            
        Returns:
            StorageResult with session data
        """
        pass
    
    @abstractmethod
    async def delete_session(self, session_id: str) -> StorageResult:
        """Delete a session"""
        pass
    
    @abstractmethod
    async def list_sessions(self, 
                           status: Optional[str] = None,
                           limit: Optional[int] = None) -> StorageResult:
        """
        List sessions
        
        Args:
            status: Filter by status (active, paused, archived)
            limit: Maximum number of sessions
            
        Returns:
            StorageResult with list of session IDs
        """
        pass
    
    @abstractmethod
    async def get_all_sessions(self) -> StorageResult:
        """
        Get all sessions
        
        Returns:
            StorageResult with dict of {session_id: data}
        """
        pass
    
    @abstractmethod
    async def count(self, status: Optional[str] = None) -> StorageResult:
        """Count sessions"""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close backend connection"""
        pass
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class CompressionBackend(ABC):
    """
    Abstract base class for compression backends
    
    Implementations: gzip, zstd, lz4, etc.
    """
    
    @property
    @abstractmethod
    def algorithm_name(self) -> str:
        """Algorithm identifier"""
        pass
    
    @property
    @abstractmethod
    def file_extension(self) -> str:
        """File extension for compressed files"""
        pass
    
    @abstractmethod
    def compress(self, data: bytes) -> bytes:
        """
        Compress data
        
        Args:
            data: Raw bytes
            
        Returns:
            Compressed bytes
        """
        pass
    
    @abstractmethod
    def decompress(self, data: bytes) -> bytes:
        """
        Decompress data
        
        Args:
            data: Compressed bytes
            
        Returns:
            Decompressed bytes
        """
        pass
    
    def compress_file(self, source_path: str, 
                      target_path: Optional[str] = None) -> StorageResult:
        """
        Compress a file
        
        Args:
            source_path: Source file path
            target_path: Target file path (optional)
            
        Returns:
            StorageResult with target path
        """
        try:
            from pathlib import Path
            
            source = Path(source_path)
            if not source.exists():
                return StorageResult.err(f"Source file not found: {source_path}")
            
            if target_path is None:
                target_path = str(source) + self.file_extension
            
            target = Path(target_path)
            
            # Read, compress, write
            data = source.read_bytes()
            compressed = self.compress(data)
            target.write_bytes(compressed)
            
            # Calculate compression ratio
            ratio = len(compressed) / len(data) if data else 0
            
            return StorageResult.ok({
                "target_path": target_path,
                "original_size": len(data),
                "compressed_size": len(compressed),
                "ratio": ratio,
            }, backend=self.algorithm_name)
            
        except Exception as e:
            return StorageResult.err(str(e), backend=self.algorithm_name)
    
    def decompress_file(self, source_path: str,
                        target_path: Optional[str] = None) -> StorageResult:
        """
        Decompress a file
        
        Args:
            source_path: Compressed file path
            target_path: Target file path (optional)
            
        Returns:
            StorageResult with target path
        """
        try:
            from pathlib import Path
            
            source = Path(source_path)
            if not source.exists():
                return StorageResult.err(f"Source file not found: {source_path}")
            
            if target_path is None:
                # Remove extension
                target_path = str(source)
                if target_path.endswith(self.file_extension):
                    target_path = target_path[:-len(self.file_extension)]
            
            target = Path(target_path)
            
            # Read, decompress, write
            data = source.read_bytes()
            decompressed = self.decompress(data)
            target.write_bytes(decompressed)
            
            return StorageResult.ok({
                "target_path": target_path,
                "compressed_size": len(data),
                "decompressed_size": len(decompressed),
            }, backend=self.algorithm_name)
            
        except Exception as e:
            return StorageResult.err(str(e), backend=self.algorithm_name)
    
    def read_compressed(self, path: str, encoding: str = 'utf-8') -> StorageResult:
        """
        Read and decompress file in one operation
        
        Args:
            path: File path
            encoding: Text encoding
            
        Returns:
            StorageResult with content string
        """
        try:
            from pathlib import Path
            
            path_obj = Path(path)
            
            if not path_obj.exists():
                return StorageResult.err(f"File not found: {path}")
            
            data = path_obj.read_bytes()
            
            # Check if compressed by extension
            if path_obj.suffix == self.file_extension:
                data = self.decompress(data)
            
            return StorageResult.ok(data.decode(encoding), backend=self.algorithm_name)
            
        except Exception as e:
            return StorageResult.err(str(e), backend=self.algorithm_name)


# Backend factory
class StorageBackendFactory:
    """Factory for creating storage backends"""
    
    _vector_backends: Dict[str, type] = {}
    _session_backends: Dict[str, type] = {}
    _compression_backends: Dict[str, type] = {}
    
    @classmethod
    def register_vector(cls, name: str, backend_class: type):
        """Register a vector storage backend"""
        cls._vector_backends[name] = backend_class
    
    @classmethod
    def register_session(cls, name: str, backend_class: type):
        """Register a session storage backend"""
        cls._session_backends[name] = backend_class
    
    @classmethod
    def register_compression(cls, name: str, backend_class: type):
        """Register a compression backend"""
        cls._compression_backends[name] = backend_class
    
    @classmethod
    def create_vector(cls, name: str, config: Dict[str, Any]) -> VectorStorageBackend:
        """Create a vector storage backend"""
        if name not in cls._vector_backends:
            raise ValueError(f"Unknown vector backend: {name}")
        return cls._vector_backends[name](config)
    
    @classmethod
    def create_session(cls, name: str, config: Dict[str, Any]) -> SessionStorageBackend:
        """Create a session storage backend"""
        if name not in cls._session_backends:
            raise ValueError(f"Unknown session backend: {name}")
        return cls._session_backends[name](config)
    
    @classmethod
    def create_compression(cls, name: str, config: Dict[str, Any]) -> CompressionBackend:
        """Create a compression backend"""
        if name not in cls._compression_backends:
            raise ValueError(f"Unknown compression backend: {name}")
        return cls._compression_backends[name](config)
    
    @classmethod
    def list_backends(cls, backend_type: Optional[StorageBackendType] = None) -> Dict[str, List[str]]:
        """List available backends"""
        return {
            "vector": list(cls._vector_backends.keys()),
            "session": list(cls._session_backends.keys()),
            "compression": list(cls._compression_backends.keys()),
        }
