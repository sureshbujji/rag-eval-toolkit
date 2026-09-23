from src.retriever import retrieve, TfIdfRetriever

CHUNKS = [
    {"id": "c1", "doc_id": "refunds",
     "text": "Issue a refund with POST /v1/refunds. Refunds take 5-10 business days."},
    {"id": "c2", "doc_id": "webhooks",
     "text": "Verify webhooks with the Nimbus-Signature HMAC-SHA256 header."},
    {"id": "c3", "doc_id": "rate-limits",
     "text": "Default quota is 100 requests per second. HTTP 429 means rate limited."},
]


def test_obviously_relevant_doc_ranks_first():
    results = retrieve("how long does a refund take", CHUNKS, k=3)
    assert results, "expected results"
    assert results[0]["chunk_id"] == "c1"
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_function_and_class_agree():
    via_fn = retrieve("webhook signature verification", CHUNKS, k=2)
    via_cls = TfIdfRetriever(CHUNKS).retrieve("webhook signature verification", k=2)
    assert via_fn == via_cls
    assert via_fn[0]["chunk_id"] == "c2"


def test_empty_query_returns_nothing():
    assert retrieve("", CHUNKS, k=3) == []


def test_k_limits_results():
    assert len(retrieve("refund webhook rate", CHUNKS, k=1)) == 1
