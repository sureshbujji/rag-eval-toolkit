"""Deterministic chunk-set drift detection (no embeddings needed).

Fingerprint: SHA-256 over the sorted per-chunk char-3-gram distributions.
Drift score: fraction of chunks in run B whose fingerprint differs from run A
(by chunk id), blended with added/removed ids — 0.0 means identical.
"""

import hashlib
from collections import Counter

_GRAM = 3


def _profile(text):
    grams = Counter(text[i:i + _GRAM] for i in range(len(text) - _GRAM + 1))
    total = sum(grams.values()) or 1
    return {g: c / total for g, c in grams.items()}


def _chunk_digest(text):
    body = "|".join(f"{g}:{v:.6f}" for g, v in sorted(_profile(text).items()))
    return hashlib.sha256(body.encode()).hexdigest()


def fingerprint(chunks):
    """Deterministic SHA-256 hex digest of the whole chunk set."""
    per_chunk = sorted((c["id"], _chunk_digest(c["text"])) for c in chunks)
    joined = "\n".join(f"{cid}:{d}" for cid, d in per_chunk)
    return hashlib.sha256(joined.encode()).hexdigest()


def compare(run_a, run_b):
    """Compare two chunk lists. Returns a drift report dict."""
    a = {c["id"]: _chunk_digest(c["text"]) for c in run_a}
    b = {c["id"]: _chunk_digest(c["text"]) for c in run_b}

    ids_a, ids_b = set(a), set(b)
    added = sorted(ids_b - ids_a)
    removed = sorted(ids_a - ids_b)
    changed = sorted(cid for cid in ids_a & ids_b if a[cid] != b[cid])

    total = max(len(ids_b), 1)
    drift_score = round((len(added) + len(removed) + len(changed)) / total, 4)
    return {
        "drift_score": drift_score,
        "fingerprint_a": fingerprint(run_a),
        "fingerprint_b": fingerprint(run_b),
        "added": added,
        "removed": removed,
        "changed": changed,
        "drifted": drift_score > 0,
    }
