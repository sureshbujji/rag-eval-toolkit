# RAG Eval Toolkit

I built this to answer a question I kept running into while evaluating AI features as a QA lead: **how do you regression-test a RAG pipeline without an LLM in the loop?**

This toolkit chunks a small docs corpus with three strategies, retrieves with a from-scratch TF-IDF scorer (stdlib only — no embeddings, no API keys), and scores the pipeline on retrieval quality (precision/recall@k), corpus drift (deterministic fingerprints), and answer faithfulness (a deterministic mock judge). Everything runs offline with `python src/run_eval.py`.

## Architecture

```
                    +------------------+
                    |  data/docs/*.md  |  10 NimbusPay API docs
                    | data/queries.jsonl|  10 labeled queries
                    +--------+---------+
                             |
              +--------------+--------------+
              |              |              |
     +--------v------+ +-----v--------+ +---v-----------+
     | fixed_size    | |sentence_aware| | overlapping   |  src/chunker.py
     +--------+------+ +-----+--------+ +---+-----------+
              |              |              |
              +--------------+--------------+
                             |
                    +--------v---------+
                    | TF-IDF retriever |  src/retriever.py (math/re/collections)
                    +--------+---------+
                             |
        +--------------------+--------------------+
        |                    |                    |
 +------v------+      +------v------+      +------v-------+
 | P/R @ k     |      | drift check |      | faithfulness |
 | src/metrics |      | src/drift   |      | src/faithful |
 +------+------+      +------+------+      +------+-------+
        |                    |                    |
        +--------------------+--------------------+
                             |
                    +--------v---------+
                    | src/run_eval.py  |
                    +--------+---------+
                             |
              +--------------+--------------+
              |                             |
   reports/rag_report.json        reports/rag_report.md
```

## Quickstart

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

pytest                 # 19 unit tests
python src/run_eval.py # end-to-end eval -> reports/
```

No API key needed — the faithfulness "judge" is a deterministic lexical checker, and drift detection uses SHA-256 fingerprints of char-3-gram profiles instead of embeddings.

## Sample output

Chunking strategy comparison (10 docs, 10 queries, k=3):

| Strategy | Chunks | P@1 | P@3 | R@3 |
|---|---|---|---|---|
| fixed_size | 20 | 0.9 | 0.5667 | 1.0 |
| sentence_aware | 20 | 0.9 | 0.5667 | 1.0 |
| overlapping | 20 | 0.9 | 0.6 | 1.0 |

Drift check catches a one-number edit (`5-10` -> `3-5 business days` in the refunds doc): drift score 0.1, changed chunks listed; identical input scores 0.0.

Faithfulness: grounded mock answers score 5/5, hallucinated ones 1-2/5, contradictions 1/5.

## Why chunking strategy matters for RAG quality

Chunking decides what the retriever can ever return — it is the ceiling on answer quality, and it fails silently:

- **Fixed-size** is cheap and predictable, but it slices mid-sentence. A fact split across a boundary ("...refunds take 5-" | "-10 business days") becomes two chunks that each score poorly and neither answers the question.
- **Sentence-aware** keeps propositions intact, so each chunk is a coherent unit of meaning. It usually wins on precision when facts live in single sentences.
- **Overlapping** hedges against boundary splits by repeating content across windows. On this corpus it edged out the others on P@3 — at the cost of a larger index and near-duplicate results.

The right choice depends on the corpus, which is exactly why I made it a measured comparison instead of a default. If you change the docs, re-run `python src/run_eval.py` and read the table.

## Roadmap

- Plug in a real embedding retriever behind the same `retrieve()` interface to compare lexical vs semantic retrieval.
- Replace the mock judge with an LLM judge behind an env-gated flag (mock stays the default so CI needs no key).
- Add MRR / nDCG metrics and a query-expansion experiment.
- Track drift reports over time (SQLite log) to catch doc regressions in CI.

## Layout

```
rag-eval-toolkit/
  data/docs/            10 sample NimbusPay API docs
  data/queries.jsonl    10 queries with doc-level relevance labels
  src/chunker.py        fixed-size / sentence-aware / overlapping
  src/retriever.py      TF-IDF from scratch (stdlib only)
  src/metrics.py        precision@k, recall@k (pure functions)
  src/drift.py          deterministic chunk-set drift detection
  src/faithfulness.py   deterministic mock faithfulness judge
  src/run_eval.py       CLI: runs the full eval, writes reports/
  tests/                19 unit tests
  reports/              generated rag_report.json / rag_report.md
```
