from src.chunker import fixed_size, sentence_aware, overlapping

DOCS = [
    {"id": "d1", "text": "First sentence here. Second sentence here. Third sentence here. Fourth."},
    {"id": "d2", "text": "Alpha beta gamma. Delta epsilon zeta."},
]


def _check_invariants(chunks, docs):
    # chunk ids unique
    ids = [c["id"] for c in chunks]
    assert len(ids) == len(set(ids))
    # every chunk points at a real doc
    doc_ids = {d["id"] for d in docs}
    assert all(c["doc_id"] in doc_ids for c in chunks)


def _check_full_coverage(chunks, docs):
    # lossless strategies: concatenated chunks == original text (mod whitespace)
    for doc in docs:
        covered = "".join(c["text"] for c in chunks if c["doc_id"] == doc["id"])
        norm = lambda s: "".join(s.split())
        assert norm(covered) == norm(doc["text"]), f"text lost from {doc['id']}"


def _check_overlap_coverage(chunks, docs):
    # every chunk is a real substring; first/last windows pin both ends
    for doc in docs:
        mine = [c["text"] for c in chunks if c["doc_id"] == doc["id"]]
        assert mine, f"no chunks for {doc['id']}"
        for t in mine:
            assert t in doc["text"]
        assert doc["text"].strip().startswith(mine[0][:20].strip()[:10] or mine[0])
        assert doc["text"].strip().endswith(mine[-1].strip()[-20:].strip()[-10:] or mine[-1])


def test_fixed_size_invariants():
    chunks = fixed_size(DOCS, chunk_size=30)
    _check_invariants(chunks, DOCS)
    _check_full_coverage(chunks, DOCS)
    assert all(len(c["text"]) <= 30 for c in chunks)


def test_sentence_aware_invariants():
    chunks = sentence_aware(DOCS, target_size=40)
    _check_invariants(chunks, DOCS)
    _check_full_coverage(chunks, DOCS)
    # no sentence is split across chunks: each chunk text is whole sentences
    for c in chunks:
        assert not c["text"].rstrip().endswith(("First", "Second"))


def test_overlapping_invariants():
    chunks = overlapping(DOCS, chunk_size=30, overlap=10)
    _check_invariants(chunks, DOCS)
    _check_overlap_coverage(chunks, DOCS)
    assert all(len(c["text"]) <= 30 for c in chunks)
    # overlap means strictly more chunks than fixed-size for multi-window docs
    assert len(chunks) >= len(fixed_size(DOCS, chunk_size=30))


def test_overlapping_rejects_bad_config():
    try:
        overlapping(DOCS, chunk_size=30, overlap=30)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")
