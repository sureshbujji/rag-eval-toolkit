"""Chunking strategies for RAG pipelines.

Each strategy takes a list of documents ``[{"id", "text"}]`` and returns a
list of chunks ``[{"id", "doc_id", "text"}]``. Chunk ids are deterministic:
``"<doc_id>:<strategy>:<index>"`` so runs are reproducible.
"""

import re

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def fixed_size(docs, chunk_size=400):
    """Character windows with no overlap."""
    chunks = []
    for doc in docs:
        text = doc["text"].strip()
        index = 0
        for start in range(0, len(text), chunk_size):
            window = text[start:start + chunk_size].strip()
            if window:
                chunks.append({
                    "id": f"{doc['id']}:fixed:{index}",
                    "doc_id": doc["id"],
                    "text": window,
                })
                index += 1
    return chunks


def sentence_aware(docs, target_size=400):
    """Split on sentence boundaries, pack sentences to a target size."""
    chunks = []
    for doc in docs:
        sentences = [s.strip() for s in _SENTENCE_SPLIT.split(doc["text"].strip())]
        sentences = [s for s in sentences if s]
        index = 0
        current = ""
        for sentence in sentences:
            candidate = f"{current} {sentence}".strip() if current else sentence
            if len(candidate) > target_size and current:
                chunks.append({
                    "id": f"{doc['id']}:sent:{index}",
                    "doc_id": doc["id"],
                    "text": current,
                })
                index += 1
                current = sentence
            else:
                current = candidate
        if current:
            chunks.append({
                "id": f"{doc['id']}:sent:{index}",
                "doc_id": doc["id"],
                "text": current,
            })
    return chunks


def overlapping(docs, chunk_size=400, overlap=100):
    """Sliding character window with configurable overlap."""
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")
    chunks = []
    for doc in docs:
        text = doc["text"].strip()
        index = 0
        start = 0
        step = chunk_size - overlap
        while start < len(text):
            window = text[start:start + chunk_size].strip()
            if window:
                chunks.append({
                    "id": f"{doc['id']}:overlap:{index}",
                    "doc_id": doc["id"],
                    "text": window,
                })
                index += 1
            if start + chunk_size >= len(text):
                break
            start += step
    return chunks
