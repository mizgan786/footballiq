"""
rag_service.py

Loads the TF-IDF retrieval index built by rag/ingest.py and exposes
retrieve() for the chat orchestrator. See rag/ingest.py for why TF-IDF
rather than a neural embedding store.
"""

import os
import joblib
from sklearn.metrics.pairwise import cosine_similarity

INDEX_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "rag", "embeddings", "index.joblib")

_index = joblib.load(INDEX_PATH)
_vectorizer = _index["vectorizer"]
_matrix = _index["matrix"]
_chunks = _index["chunks"]


def retrieve(query: str, top_k: int = 3, min_score: float = 0.08):
    """Returns up to top_k knowledge-base chunks relevant to query, each
    above min_score cosine similarity. Returns [] for queries that don't
    match the knowledge base at all (e.g. pure player-stat questions) -
    callers should not inject irrelevant context into the prompt."""
    query_vec = _vectorizer.transform([query])
    scores = cosine_similarity(query_vec, _matrix)[0]

    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
    results = []
    for idx, score in ranked[:top_k]:
        if score < min_score:
            continue
        chunk = _chunks[idx]
        results.append({"source": chunk["source"], "title": chunk["title"], "text": chunk["text"], "score": float(score)})
    return results
