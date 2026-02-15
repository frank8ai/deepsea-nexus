"""Legacy vector store wrapper.

The codebase currently contains two vector store implementations:
- `vector_store/` (legacy v2-style modules expecting a config_path)
- `vector_store.py` (lightweight, direct Chroma PersistentClient wrapper)

For vNext stability, plugins should use this wrapper so we can evolve internals
without breaking the plugin surface.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

# NOTE: deepsea_nexus has both `vector_store/` (package) and `vector_store.py` (module).
# Import explicitly from the file-module to avoid package name shadowing.
import importlib.util
from pathlib import Path

_mod_path = Path(__file__).with_name("vector_store.py")
_spec = importlib.util.spec_from_file_location("deepsea_nexus._vector_store_file", _mod_path)
assert _spec and _spec.loader
_vector_store_file = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_vector_store_file)  # type: ignore[attr-defined]
VectorStore = _vector_store_file.VectorStore


def create_vector_store(config: Optional[Dict[str, Any]] = None) -> VectorStore:
    # Accept the full app config dict; `VectorStore` handles defaults.
    persist_path = None
    collection = "deepsea_nexus"

    if isinstance(config, dict):
        nexus_cfg = config.get("nexus", {}) if isinstance(config.get("nexus", {}), dict) else {}
        persist_path = nexus_cfg.get("vector_db_path")
        collection = nexus_cfg.get("collection_name") or collection

    return VectorStore(collection_name=collection, persist_path=persist_path)
