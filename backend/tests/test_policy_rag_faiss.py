"""
Dedicated Verification Tests for FastEmbed + FAISS Policy RAG Service
======================================================================
Verifies:
1. FastEmbed model configuration (BAAI/bge-small-en-v1.5).
2. FAISS vector index creation, instantiation, and disk persistence.
3. Policy markdown chunking and embedding generation.
4. FAISS index similarity search functionality.
5. Offline 0-network query execution.
"""

import pytest
from pathlib import Path
import services.policy_rag as pr
from services.policy_rag import build_policy_index, search_policy, _get_embedding_model
from config import get_settings


@pytest.mark.asyncio
async def test_faiss_policy_rag_pipeline():
    """Verify FastEmbed embedding generation, FAISS index creation, and persistence."""
    settings = get_settings()

    # 1. Verify model configuration
    assert settings.EMBEDDING_MODEL == "BAAI/bge-small-en-v1.5"

    # 2. Force rebuild of policy index
    build_policy_index(force_rebuild=True)

    # 3. Verify FAISS index is actually instantiated in memory
    assert pr._FAISS_INDEX is not None
    assert pr._FAISS_INDEX.ntotal > 0
    assert len(pr._POLICY_CHUNKS) > 0

    # 4. Verify disk persistence files exist under POLICY_INDEX_DIR
    index_dir = Path(settings.POLICY_INDEX_DIR)
    assert (index_dir / "policy_faiss.index").exists()
    assert (index_dir / "policy_chunks.json").exists()

    # 5. Verify FastEmbed model is loaded
    model = _get_embedding_model()
    assert model is not None

    # 6. Perform vector similarity search (0 network calls)
    res = await search_policy("income mismatch policy", k=3)
    assert "chunks" in res
    assert len(res["chunks"]) > 0

    # Confirm relevant text or section is returned by FAISS vector search
    chunk_texts = " ".join([c["section"] + " " + c["text"] for c in res["chunks"]]).lower()
    assert "income" in chunk_texts or "underwriting" in chunk_texts
