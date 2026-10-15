"""
ingest.py

Chunking -> embeddings -> vector index, per the spec's RAG pipeline -
implemented with a lightweight, fully local TF-IDF index rather than a
neural embedding model or a full vector database (ChromaDB/FAISS).

Why: the knowledge base here is a handful of short reference documents
(a few KB total), not a large corpus. A neural embedding model adds a
real dependency (sentence-transformers / an API call per chunk) for no
retrieval-quality benefit at this scale, and this sandbox's network
can't reach model-hosting domains anyway. TF-IDF + cosine similarity is
the right-sized tool here: zero external calls, deterministic, and
fast. This module can be swapped for a ChromaDB/FAISS + real embeddings
backend later without changing the retrieval interface
(rag_service.retrieve()) that the rest of the app depends on.

Chunking: split each markdown doc on its "## " headers, so each chunk
is one self-contained topic (e.g. "xG (Expected Goals)") rather than an
arbitrary character-count window.

Run: python rag/ingest.py
"""

import os
import re
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

DOCS_DIR = os.path.join(os.path.dirname(__file__), "documents")
INDEX_PATH = os.path.join(os.path.dirname(__file__), "embeddings", "index.joblib")


def chunk_document(filepath: str):
    with open(filepath, encoding="utf-8") as f:
        text = f.read()
    filename = os.path.basename(filepath)

    doc_title_match = re.match(r"# (.+)", text)
    doc_title = doc_title_match.group(1) if doc_title_match else filename

    # split on "## " section headers, keeping the header with its content
    sections = re.split(r"\n(?=## )", text)
    chunks = []
    for i, section in enumerate(sections):
        section = section.strip()
        if not section:
            continue
        if i == 0:
            # intro section: strip the "# Doc Title" line but keep any body
            # text under it as its own chunk (this used to be silently
            # dropped entirely - it can contain real content, e.g. the
            # leagues list in competitions.md)
            body = re.sub(r"^# .+\n?", "", section).strip()
            if not body:
                continue
            chunks.append({"source": filename, "title": doc_title, "text": f"{doc_title}\n\n{body}"})
            continue
        title_match = re.match(r"## (.+)", section)
        title = title_match.group(1) if title_match else filename
        chunks.append({"source": filename, "title": title, "text": section})
    return chunks


def main():
    all_chunks = []
    for filename in sorted(os.listdir(DOCS_DIR)):
        if filename.endswith(".md"):
            all_chunks.extend(chunk_document(os.path.join(DOCS_DIR, filename)))

    texts = [c["text"] for c in all_chunks]
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=5000)
    matrix = vectorizer.fit_transform(texts)

    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    joblib.dump({"vectorizer": vectorizer, "matrix": matrix, "chunks": all_chunks}, INDEX_PATH)

    print(f"Indexed {len(all_chunks)} chunks from {len(os.listdir(DOCS_DIR))} documents -> {INDEX_PATH}")
    for c in all_chunks:
        print(f"  - [{c['source']}] {c['title']}")


if __name__ == "__main__":
    main()
