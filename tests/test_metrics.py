from src.metrics import precision_at_k, recall_at_k, evaluate

# Hand-computed fixture: retrieved [d1, d2, d3], relevant {d1, d3}.
RETRIEVED = ["d1", "d2", "d3"]
RELEVANT = ["d1", "d3"]


def test_precision_at_k():
    assert precision_at_k(RETRIEVED, RELEVANT, 1) == 1.0      # d1 hit
    assert precision_at_k(RETRIEVED, RELEVANT, 2) == 0.5      # d1 hit, d2 miss
    assert precision_at_k(RETRIEVED, RELEVANT, 3) == 2 / 3


def test_recall_at_k():
    assert recall_at_k(RETRIEVED, RELEVANT, 1) == 0.5          # only d1 of 2 found
    assert recall_at_k(RETRIEVED, RELEVANT, 3) == 1.0


def test_edge_cases():
    assert precision_at_k([], RELEVANT, 3) == 0.0
    assert recall_at_k(RETRIEVED, [], 3) == 0.0
    assert precision_at_k(RETRIEVED, RELEVANT, 0) == 0.0


def test_evaluate_means():
    # q1: perfect at 1; q2: retrieved [d9], relevant {d1} -> 0 everywhere
    results = [(["d1", "d2"], ["d1"]), (["d9"], ["d1"])]
    out = evaluate(results, ks=(1, 2))
    assert out["precision@1"] == 0.5
    assert out["recall@1"] == 0.5
    assert out["precision@2"] == 0.25  # (0.5 + 0.0) / 2
    assert out["recall@2"] == 0.5
