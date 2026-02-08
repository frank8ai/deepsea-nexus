"""
Deep-Sea Nexus v2.0 - Main Driver

This module provides the main interface for the Deep-Sea Nexus memory system.
"""

from typing import Dict, Any, Optional
import os
import yaml


class DeepSeaNexus:
    """
    Main interface for Deep-Sea Nexus v2.0 memory system.
    
    Usage:
        nexus = DeepSeaNexus()
        
        # Index a note
        nexus.index_note(content, metadata)
        
        # Recall relevant information
        results = nexus.recall("query")
        
        # Get RAG context
        context = nexus.get_rag_context("question")
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize Deep-Sea Nexus.
        
        Args:
            config_path: Optional path to config.yaml
        """
        self.config_path = config_path
        self.config = self._load_config()
        
        # Lazy initialization
        self._store = None
        self._manager = None
        self._recall = None
        self._rag = None
        self._splitter = None
        
    def _load_config(self) -> dict:
        """Load configuration."""
        if self.config_path is None:
            self.config_path = os.path.join(
                os.path.dirname(__file__),
                'config.yaml'
            )
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _ensure_initialized(self):
        """Ensure all components are initialized."""
        if self._store is None:
            from vector_store.init_chroma import create_vector_store
            self._store = create_vector_store(self.config_path)
            
        if self._manager is None:
            from vector_store.manager import create_manager
            self._manager = create_manager(
                self._store.embedder,
                self._store.collection,
                self.config_path
            )
            
        if self._recall is None:
            from retrieval.semantic_recall import create_semantic_recall
            self._recall = create_semantic_recall(
                self._manager,
                self.config_path
            )
            
        if self._rag is None:
            from retrieval.rag_integrator import create_rag_integrator
            self._rag = create_rag_integrator(
                self._recall,
                self.config_path
            )
            
        if self._splitter is None:
            from chunking.text_splitter import create_splitter
            self._splitter = create_splitter(self.config_path)
    
    # ==================== Indexing Methods ====================
    
    def index_note(
        self,
        content: str,
        metadata: Dict[str, Any] = None,
        strategy: str = "hybrid"
    ) -> str:
        """
        Index a single note.
        
        Args:
            content: Note content
            metadata: Metadata dict
            strategy: Chunking strategy
            
        Returns:
            Document ID
        """
        self._ensure_initialized()
        
        # Chunk the content
        chunks = self._splitter.chunk_document(
            text=content,
            document_metadata=metadata or {},
            strategy=strategy
        )
        
        # Add to vector store
        ids = self._manager.add_notes_batch(chunks)
        
        return ids[0] if ids else None
    
    def index_file(
        self,
        file_path: str,
        metadata: Dict[str, Any] = None,
        strategy: str = "hybrid"
    ) -> Dict[str, Any]:
        """
        Index a file.
        
        Args:
            file_path: Path to file
            metadata: Additional metadata
            strategy: Chunking strategy
            
        Returns:
            Indexing result with chunk count
        """
        self._ensure_initialized()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Build metadata
        file_metadata = {
            "source_file": file_path,
            "title": os.path.basename(file_path),
            "type": "file"
        }
        
        if metadata:
            file_metadata.update(metadata)
        
        # Index
        chunks = self._splitter.chunk_document(
            text=content,
            document_metadata=file_metadata,
            strategy=strategy
        )
        
        ids = self._manager.add_notes_batch(chunks)
        
        return {
            "file": file_path,
            "chunks": len(chunks),
            "ids": ids
        }
    
    # ==================== Recall Methods ====================
    
    def recall(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        Recall relevant notes.
        
        Args:
            query: Search query
            top_k: Number of results
            threshold: Minimum similarity score
            
        Returns:
            Recall results
        """
        self._ensure_initialized()
        
        from retrieval.semantic_recall import RecallContext
        result = self._recall.recall(
            query=query,
            top_k=top_k,
            threshold=threshold
        )
        
        return result.to_dict()
    
    def recall_with_context(
        self,
        query: str,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Recall with formatted context.
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            Context and sources
        """
        self._ensure_initialized()
        return self._recall.recall_with_context(query, top_k=top_k)
    
    # ==================== RAG Methods ====================
    
    def get_rag_context(
        self,
        question: str,
        system_prompt: str = None
    ) -> Dict[str, Any]:
        """
        Get RAG context for a question.
        
        Args:
            question: User question
            system_prompt: Optional custom system prompt
            
        Returns:
            Context ready for LLM
        """
        self._ensure_initialized()
        
        context = self._rag.prepare_context(
            query=question,
            system_prompt=system_prompt
        )
        
        return {
            "question": question,
            "context": context.retrieved_context,
            "sources": context.sources
        }
    
    def answer(
        self,
        question: str,
        llm_provider = None
    ) -> Dict[str, Any]:
        """
        Answer a question using RAG.
        
        Args:
            question: User question
            llm_provider: Optional LLM function
            
        Returns:
            Answer with sources
        """
        self._ensure_initialized()
        return self._rag.answer_question(question, llm_provider)
    
    # ==================== Management Methods ====================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        self._ensure_initialized()
        return self._manager.get_stats()
    
    def search(
        self,
        query: str,
        n_results: int = 5
    ) -> Dict[str, Any]:
        """
        Search notes.
        
        Args:
            query: Search query
            n_results: Number of results
            
        Returns:
            Search results
        """
        self._ensure_initialized()
        return self._manager.search(query, n_results=n_results)
    
    def delete_by_id(self, doc_id: str) -> bool:
        """Delete a document by ID."""
        self._ensure_initialized()
        return self._manager.delete_by_id(doc_id)
    
    def reset(self):
        """Reset the vector store."""
        self._ensure_initialized()
        self._manager.reset_collection()
        
        # Reset instances
        self._store = None
        self._manager = None
        self._recall = None
        self._rag = None


def create_nexus(config_path: str = None) -> DeepSeaNexus:
    """Factory function to create DeepSeaNexus instance."""
    return DeepSeaNexus(config_path)


# Convenience function for quick usage
def quick_recall(query: str, config_path: str = None) -> Dict[str, Any]:
    """
    Quick recall without full initialization.
    
    Args:
        query: Search query
        config_path: Optional config path
        
    Returns:
        Recall results
    """
    nexus = create_nexus(config_path)
    return nexus.recall(query)


if __name__ == "__main__":
    # Example usage
    nexus = create_nexus()
    
    print("=" * 50)
    print("Deep-Sea Nexus v2.0")
    print("=" * 50)
    
    # Check stats
    stats = nexus.get_stats()
    print(f"\nStatus:")
    print(f"  Documents: {stats['total_documents']}")
    print(f"  Collection: {stats['collection_name']}")
    
    # Quick test recall
    print("\nTest recall:")
    results = nexus.recall("memory system", top_k=3)
    print(f"Found: {results.get('total_found', 0)} results")
