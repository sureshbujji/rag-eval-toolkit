# RAG Eval Report

Generated: 2026-09-23T03:58:16.331538+00:00

Corpus: 10 docs, 10 queries, k=3

## Chunking strategy comparison

| Strategy | Chunks | P@1 | P@3 | P@5 | R@1 | R@3 | R@5 |
|---|---|---|---|---|---|---|---|
| fixed_size | 20 | 0.9 | 0.5667 | 0.5667 | 0.8 | 1.0 | 1.0 |
| sentence_aware | 20 | 0.9 | 0.5667 | 0.5667 | 0.8 | 1.0 | 1.0 |
| overlapping | 20 | 0.9 | 0.6 | 0.6 | 0.8 | 1.0 | 1.0 |

**Best by P@3:** overlapping

## Drift check (sentence_aware)

Perturbed run drift score: 0.1 (changed=['refunds:sent:0', 'webhooks:sent:1'], added=[], removed=[])
Identical run drift score: 0.0 (drifted=False)

## Faithfulness (mock judge, 1-5)

- Q: How do I verify a webhook signature?
  - grounded answer: 5/5 (2 claims)
  - ungrounded answer: 2/5 (2 claims)
- Q: What happens when I exceed the rate limit?
  - grounded answer: 5/5 (3 claims)
  - ungrounded answer: 2/5 (2 claims)
- Q: How long do payouts take?
  - grounded answer: 5/5 (2 claims)
  - ungrounded answer: 1/5 (1 claims)
