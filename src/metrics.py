"""Retrieval quality metrics. Pure functions, no I/O."""


def precision_at_k(retrieved_doc_ids, relevant_doc_ids, k):
    """Fraction of the top-k retrieved docs that are relevant."""
    if k <= 0:
        return 0.0
    retrieved = retrieved_doc_ids[:k]
    relevant = set(relevant_doc_ids)
    hits = sum(1 for d in retrieved if d in relevant)
    return hits / min(k, len(retrieved)) if retrieved else 0.0


def recall_at_k(retrieved_doc_ids, relevant_doc_ids, k):
    """Fraction of relevant docs found in the top-k retrieved docs."""
    relevant = set(relevant_doc_ids)
    if not relevant:
        return 0.0
    retrieved = set(retrieved_doc_ids[:k])
    return len(retrieved & relevant) / len(relevant)


def mean_metric(results, metric_fn, k):
    """Mean of a metric over per-query ``(retrieved, relevant)`` pairs."""
    if not results:
        return 0.0
    return sum(metric_fn(r, rel, k) for r, rel in results) / len(results)


def evaluate(results, ks=(1, 3, 5)):
    """Mean precision/recall at each k over all queries.

    ``results``: iterable of ``(retrieved_doc_ids, relevant_doc_ids)``.
    """
    results = list(results)
    return {
        f"precision@{k}": round(mean_metric(results, precision_at_k, k), 4)
        for k in ks
    } | {
        f"recall@{k}": round(mean_metric(results, recall_at_k, k), 4)
        for k in ks
    }
