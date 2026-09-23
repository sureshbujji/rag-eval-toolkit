"""TF-IDF retriever implemented from scratch (stdlib only).

Scoring: sublinear term frequency * smoothed idf, cosine-normalized by
chunk length. Documents are indexed once per call; keep it simple and
stateless so the eval loop can swap chunking strategies freely.
"""

import math
import re
from collections import Counter

_TOKEN = re.compile(r"[a-z0-9]+")


def tokenize(text):
    return _TOKEN.findall(text.lower())


class TfIdfRetriever:
    def __init__(self, chunks):
        self.chunks = chunks
        self.doc_ids = [c["id"] for c in chunks]
        self.term_freqs = [Counter(tokenize(c["text"])) for c in chunks]
        self.lengths = [sum(tf.values()) for tf in self.term_freqs]

        # Document frequency per term -> idf over the chunk corpus.
        n = len(chunks)
        df = Counter()
        for tf in self.term_freqs:
            for term in tf:
                df[term] += 1
        self.idf = {t: math.log((n + 1) / (d + 1)) + 1.0 for t, d in df.items()}

    def _weights(self, tf, length):
        weights = {}
        for term, count in tf.items():
            idf = self.idf.get(term, 0.0)
            if idf > 0:
                sub_tf = 1.0 + math.log(count)  # sublinear tf
                weights[term] = (sub_tf * idf) / length  # length normalization
        return weights

    def retrieve(self, query, k=5):
        """Return ``[{"chunk_id", "score"}]`` ranked by cosine similarity."""
        qtf = Counter(tokenize(query))
        qw = self._weights(qtf, max(1, sum(qtf.values())))
        qnorm = math.sqrt(sum(w * w for w in qw.values()))
        if qnorm == 0:
            return []

        scored = []
        for i, tf in enumerate(self.term_freqs):
            dw = self._weights(tf, max(1, self.lengths[i]))
            dot = sum(qw[t] * dw.get(t, 0.0) for t in qw)
            dnorm = math.sqrt(sum(w * w for w in dw.values()))
            score = dot / (qnorm * dnorm) if dnorm else 0.0
            if score > 0:
                scored.append((self.doc_ids[i], score))
        scored.sort(key=lambda x: (-x[1], x[0]))  # deterministic tie-break
        return [{"chunk_id": cid, "score": round(s, 6)} for cid, s in scored[:k]]


def retrieve(query, chunks, k=5):
    """Stateless convenience wrapper: index chunks, run one query."""
    return TfIdfRetriever(chunks).retrieve(query, k)
