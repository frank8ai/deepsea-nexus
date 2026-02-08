"""
Deep-Sea Nexus v2.0
===================

A vector-based memory system with RAG capabilities for AI agents.

Installation:
    pip install -r requirements.txt

Usage:
    from DEEP_SEA_NEXUS_V2 import create_nexus
    
    # Initialize
    nexus = create_nexus()
    
    # Index a note
    nexus.index_note(content, metadata)
    
    # Recall relevant information
    results = nexus.recall("query")
    
    # Get RAG context
    context = nexus.get_rag_context("question")

Modules:
    - vector_store: ChromaDB initialization and management
    - chunking: Text splitting and chunking
    - retrieval: Semantic search and RAG
    - scripts: Automation tools
"""

__version__ = "2.0.0"
__author__ = "Deep-Sea Nexus Team"

from . import create_nexus, quick_recall

__all__ = [
    "create_nexus",
    "quick_recall"
]
