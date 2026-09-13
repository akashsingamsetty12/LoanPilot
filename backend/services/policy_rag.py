"""
Policy RAG Service
==================
Local Retrieval-Augmented Generation (RAG) service for lending policies using FastEmbed and FAISS.

Cognizant Explainability Note:
- Index Build Time: Policy documents in backend/data/policies/ are chunked by section/paragraph,
  embedded locally with BAAI/bge-small-en-v1.5 via FastEmbed, and persisted as a FAISS IndexFlatIP
  plus JSON metadata under POLICY_INDEX_DIR.
- First-time Load Note: FastEmbed downloads the ONNX model files on first invocation if not present in cache.
- Query Time: search_policy() embeds the query locally and performs FAISS vector search with 0 network calls.
- Event Loop Offloading: Vector embedding inference and FAISS search are offloaded to threadpools
  via starlette.concurrency.run_in_threadpool so CPU calculation never blocks FastAPI.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
import faiss
from fastembed import TextEmbedding
from starlette.concurrency import run_in_threadpool
from config import get_settings

logger = logging.getLogger("loanpilot.policy_rag")

# Persistent policy store in memory
_EMBEDDING_MODEL_INSTANCE: Optional[TextEmbedding] = None
_FAISS_INDEX: Optional[faiss.Index] = None
_POLICY_CHUNKS: List[Dict[str, Any]] = []
_INDEX_BUILT = False


def _get_embedding_model() -> TextEmbedding:
    """
    Lazy initializer for FastEmbed model.
    First call downloads/caches BAAI/bge-small-en-v1.5 locally if not present.
    Subsequent query-time calls use cached model locally with 0 network calls.
    """
    global _EMBEDDING_MODEL_INSTANCE
    if _EMBEDDING_MODEL_INSTANCE is None:
        settings = get_settings()
        logger.info(f"Initializing FastEmbed TextEmbedding with model: {settings.EMBEDDING_MODEL}")
        _EMBEDDING_MODEL_INSTANCE = TextEmbedding(model_name=settings.EMBEDDING_MODEL)
    return _EMBEDDING_MODEL_INSTANCE


def _extract_chunks_from_file(file_path: Path) -> List[Dict[str, Any]]:
    """Reads a markdown policy file and chunks it cleanly by section headers and paragraphs."""
    chunks = []
    if not file_path.exists():
        return chunks

    raw_text = file_path.read_text(encoding="utf-8").replace("\r\n", "\n")
    current_section = file_path.stem.replace("_", " ").title()
    current_para = []

    for line in raw_text.splitlines():
        stripped = line.strip()
        if not stripped:
            if current_para:
                chunks.append({
                    "text": " ".join(current_para),
                    "source": file_path.name,
                    "section": current_section
                })
                current_para = []
        elif stripped.startswith("#"):
            if current_para:
                chunks.append({
                    "text": " ".join(current_para),
                    "source": file_path.name,
                    "section": current_section
                })
                current_para = []
            current_section = stripped.lstrip("#").strip()
        else:
            current_para.append(stripped)

    if current_para:
        chunks.append({
            "text": " ".join(current_para),
            "source": file_path.name,
            "section": current_section
        })

    return chunks


def build_policy_index(force_rebuild: bool = False):
    """
    Builds and loads the policy RAG index from local policy markdown files.
    Generates embeddings using FastEmbed (BAAI/bge-small-en-v1.5) and builds a FAISS index.
    Persists faiss.index and policy_chunks.json metadata under POLICY_INDEX_DIR.
    """
    global _FAISS_INDEX, _POLICY_CHUNKS, _INDEX_BUILT

    settings = get_settings()
    policies_dir = Path(settings.POLICY_RAG_DIR)
    index_dir = Path(settings.POLICY_INDEX_DIR)
    index_dir.mkdir(parents=True, exist_ok=True)

    index_file = index_dir / "policy_faiss.index"
    chunks_file = index_dir / "policy_chunks.json"

    # Attempt loading from local disk persistence if available
    if not force_rebuild and index_file.exists() and chunks_file.exists():
        try:
            logger.info(f"Loading persisted FAISS index from {index_file}")
            _FAISS_INDEX = faiss.read_index(str(index_file))
            _POLICY_CHUNKS = json.loads(chunks_file.read_text(encoding="utf-8"))
            _INDEX_BUILT = True
            logger.info(f"Successfully restored FAISS index with {_FAISS_INDEX.ntotal} vectors.")
            return
        except Exception as e:
            logger.warning(f"Failed to load persisted FAISS index: {e}. Rebuilding index.")

    if not policies_dir.exists():
        logger.warning(f"Policies directory {policies_dir} does not exist. Creating default directory.")
        policies_dir.mkdir(parents=True, exist_ok=True)

    all_chunks = []
    for policy_file in sorted(policies_dir.glob("*.md")):
        file_chunks = _extract_chunks_from_file(policy_file)
        all_chunks.extend(file_chunks)

    if not all_chunks:
        logger.warning("No policy chunks found to build FAISS index.")
        _POLICY_CHUNKS = []
        _INDEX_BUILT = True
        return

    # Generate local embeddings via FastEmbed
    model = _get_embedding_model()
    texts = [f"{c['section']}: {c['text']}" for c in all_chunks]
    embeddings_generator = model.embed(texts)
    embeddings_list = list(embeddings_generator)
    embeddings = np.array(embeddings_list, dtype=np.float32)

    # Normalize L2 for Cosine Similarity inside FAISS IndexFlatIP
    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    _FAISS_INDEX = index
    _POLICY_CHUNKS = all_chunks
    _INDEX_BUILT = True

    # Persist FAISS index and chunk metadata to disk
    faiss.write_index(_FAISS_INDEX, str(index_file))
    chunks_file.write_text(json.dumps(all_chunks, indent=2), encoding="utf-8")
    logger.info(f"Successfully created and persisted FAISS index with {len(all_chunks)} policy vectors (dim={dimension}).")


def _sync_search_policy(query: str, k: int = 3) -> Dict[str, Any]:
    """
    Synchronous CPU vector similarity search against loaded FAISS index.
    Operates 100% locally with 0 network calls at query time.
    """
    global _FAISS_INDEX, _POLICY_CHUNKS, _INDEX_BUILT

    if not _INDEX_BUILT or _FAISS_INDEX is None:
        build_policy_index()

    if not _POLICY_CHUNKS or _FAISS_INDEX is None or _FAISS_INDEX.ntotal == 0:
        return {"chunks": []}

    model = _get_embedding_model()
    query_embeddings = list(model.embed([query]))
    query_vector = np.array(query_embeddings, dtype=np.float32)
    faiss.normalize_L2(query_vector)

    k_actual = min(k, _FAISS_INDEX.ntotal)
    distances, indices = _FAISS_INDEX.search(query_vector, k_actual)

    results = []
    if len(indices) > 0:
        for idx in indices[0]:
            if 0 <= idx < len(_POLICY_CHUNKS):
                results.append(_POLICY_CHUNKS[idx])

    return {"chunks": results}


async def search_policy(query: str, k: int = 3) -> Dict[str, Any]:
    """
    Search policy documents for guidance relevant to a query using FAISS vector search.

    Cognizant Explainability Guarantee:
    - Executed off the FastAPI event loop via run_in_threadpool.
    - Zero network calls at query time. Operates 100% offline.
    """
    return await run_in_threadpool(_sync_search_policy, query, k)

