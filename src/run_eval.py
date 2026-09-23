"""CLI orchestrator: chunk -> retrieve -> score -> drift-check -> judge.

Runs fully offline in mock mode (no API keys). Writes
``reports/rag_report.json`` and ``reports/rag_report.md``.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chunker import fixed_size, sentence_aware, overlapping  # noqa: E402
from retriever import TfIdfRetriever  # noqa: E402
from metrics import evaluate  # noqa: E402
from drift import compare as drift_compare  # noqa: E402
from faithfulness import judge  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
REPORTS = os.path.join(ROOT, "reports")

STRATEGIES = {
    "fixed_size": lambda docs: fixed_size(docs, chunk_size=400),
    "sentence_aware": lambda docs: sentence_aware(docs, target_size=400),
    "overlapping": lambda docs: overlapping(docs, chunk_size=400, overlap=100),
}

# 3 mock Q&A pairs: (query, grounded_answer, ungrounded_answer)
QA_PAIRS = [
    ("How do I verify a webhook signature?",
     "Verify webhooks by computing HMAC-SHA256 of the raw request body with "
     "your webhook secret, then compare it against the Nimbus-Signature header "
     "in constant time. Your endpoint must respond with HTTP 200 within 5 seconds.",
     "Webhooks are verified with RSA-2048 signatures inside the merchant dashboard. "
     "No response code is required from your endpoint."),
    ("What happens when I exceed the rate limit?",
     "The API returns HTTP 429 with a Retry-After header. Implement exponential "
     "backoff with jitter when calls fail. The default quota is 100 requests "
     "per second.",
     "Rate limits never trigger errors because NimbusPay queues excess traffic "
     "indefinitely for free. The quota is one million requests per second."),
    ("How long do payouts take?",
     "Payouts arrive in 2 business days for US banks and 3-5 business days "
     "internationally. The minimum payout amount is $1.00.",
     "All payouts are instant worldwide and there is no minimum amount."),
]


def load_docs():
    docs = []
    docs_dir = os.path.join(DATA, "docs")
    for fname in sorted(os.listdir(docs_dir)):
        if fname.endswith(".md"):
            with open(os.path.join(docs_dir, fname)) as f:
                docs.append({"id": fname[:-3], "text": f.read()})
    return docs


def load_queries():
    queries = []
    with open(os.path.join(DATA, "queries.jsonl")) as f:
        for line in f:
            line = line.strip()
            if line:
                queries.append(json.loads(line))
    return queries


def perturb(docs):
    """Slightly modified copy of the corpus to demonstrate drift detection."""
    copy = [dict(d) for d in docs]
    for d in copy:
        if d["id"] == "refunds":
            d["text"] = d["text"].replace(
                "5-10 business days", "3-5 business days")
        if d["id"] == "webhooks":
            d["text"] += "\n\nNote: signature version 2 is rolling out in Q4."
    return copy


def main():
    parser = argparse.ArgumentParser(description="RAG eval toolkit (mock mode)")
    parser.add_argument("--k", type=int, default=3, help="top-k for retrieval")
    parser.add_argument("--out", default=REPORTS, help="report output dir")
    args = parser.parse_args()

    docs = load_docs()
    queries = load_queries()
    os.makedirs(args.out, exist_ok=True)

    strategies_report = {}
    best = {"name": None, "precision@3": -1.0}
    for name, fn in STRATEGIES.items():
        chunks = fn(docs)
        by_id = {c["id"]: c for c in chunks}
        retriever = TfIdfRetriever(chunks)
        pairs = []
        for q in queries:
            hits = retriever.retrieve(q["query"], k=args.k)
            retrieved_docs = [by_id[h["chunk_id"]]["doc_id"] for h in hits]
            pairs.append((retrieved_docs, q["relevant_doc_ids"]))
        scores = evaluate(pairs, ks=(1, 3, 5))
        strategies_report[name] = {
            "num_chunks": len(chunks),
            "metrics": scores,
        }
        if scores["precision@3"] > best["precision@3"]:
            best = {"name": name, "precision@3": scores["precision@3"]}

    # Drift check: baseline vs perturbed corpus (sentence-aware).
    baseline = sentence_aware(docs, target_size=400)
    drifted = sentence_aware(perturb(docs), target_size=400)
    drift_report = drift_compare(baseline, drifted)
    no_drift = drift_compare(baseline, sentence_aware(docs, target_size=400))

    # Faithfulness: judge grounded vs ungrounded mock answers.
    faith_chunks = sentence_aware(docs, target_size=400)
    faith_retriever = TfIdfRetriever(faith_chunks)
    by_id = {c["id"]: c for c in faith_chunks}
    faith_results = []
    for query, grounded, ungrounded in QA_PAIRS:
        ctx = [by_id[h["chunk_id"]] for h in
               faith_retriever.retrieve(query, k=5)]  # wider context for the judge
        g, u = judge(grounded, ctx), judge(ungrounded, ctx)
        faith_results.append({
            "query": query,
            "grounded_answer_score": g["score"],
            "grounded_claims": g["claims"],
            "ungrounded_answer_score": u["score"],
            "ungrounded_claims": u["claims"],
        })

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "corpus": {"num_docs": len(docs), "num_queries": len(queries)},
        "retrieval_k": args.k,
        "strategies": strategies_report,
        "best_strategy_by_precision_at_3": best["name"],
        "drift": {
            "perturbed_run": drift_report,
            "identical_run": {
                "drift_score": no_drift["drift_score"],
                "drifted": no_drift["drifted"],
            },
        },
        "faithfulness": faith_results,
    }

    json_path = os.path.join(args.out, "rag_report.json")
    with open(json_path, "w") as f:
        json.dump(report, f, indent=2)

    lines = ["# RAG Eval Report", "",
             f"Generated: {report['generated_at']}", "",
             f"Corpus: {len(docs)} docs, {len(queries)} queries, k={args.k}", "",
             "## Chunking strategy comparison", "",
             "| Strategy | Chunks | P@1 | P@3 | P@5 | R@1 | R@3 | R@5 |",
             "|---|---|---|---|---|---|---|---|"]
    for name, s in strategies_report.items():
        m = s["metrics"]
        lines.append(
            f"| {name} | {s['num_chunks']} | {m['precision@1']} | "
            f"{m['precision@3']} | {m['precision@5']} | {m['recall@1']} | "
            f"{m['recall@3']} | {m['recall@5']} |")
    lines += ["", f"**Best by P@3:** {best['name']}", "",
              "## Drift check (sentence_aware)", "",
              f"Perturbed run drift score: {drift_report['drift_score']} "
              f"(changed={drift_report['changed']}, added={drift_report['added']}, "
              f"removed={drift_report['removed']})",
              f"Identical run drift score: {no_drift['drift_score']} "
              f"(drifted={no_drift['drifted']})", "",
              "## Faithfulness (mock judge, 1-5)", ""]
    for r in faith_results:
        lines.append(
            f"- Q: {r['query']}\n"
            f"  - grounded answer: {r['grounded_answer_score']}/5 "
            f"({r['grounded_claims']} claims)\n"
            f"  - ungrounded answer: {r['ungrounded_answer_score']}/5 "
            f"({r['ungrounded_claims']} claims)")
    md_path = os.path.join(args.out, "rag_report.md")
    with open(md_path, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Wrote {json_path} and {md_path}")
    print(f"Best strategy by P@3: {best['name']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
