from src.drift import fingerprint, compare

A = [
    {"id": "c1", "doc_id": "d1", "text": "Refunds take five to ten business days."},
    {"id": "c2", "doc_id": "d1", "text": "Webhooks need a 200 response in five seconds."},
]


def test_no_drift_on_identical_input():
    b = [dict(c) for c in A]
    report = compare(A, b)
    assert report["drift_score"] == 0.0
    assert report["drifted"] is False
    assert report["added"] == report["removed"] == report["changed"] == []
    assert report["fingerprint_a"] == report["fingerprint_b"]


def test_detects_changed_chunk():
    b = [dict(c) for c in A]
    b[0]["text"] = "Refunds take three to five business days."
    report = compare(A, b)
    assert report["drift_score"] > 0
    assert report["drifted"] is True
    assert report["changed"] == ["c1"]


def test_detects_added_and_removed():
    b = [{"id": "c1", "doc_id": "d1", "text": A[0]["text"]},
         {"id": "c3", "doc_id": "d2", "text": "Brand new chunk text here."}]
    report = compare(A, b)
    assert report["added"] == ["c3"]
    assert report["removed"] == ["c2"]
    assert report["changed"] == []


def test_fingerprint_is_deterministic():
    assert fingerprint(A) == fingerprint([dict(c) for c in A])
