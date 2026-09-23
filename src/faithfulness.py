"""Mock faithfulness judge (deterministic, no API calls).

Splits a candidate answer into sentences (claims) and checks each claim
against the retrieved context *sentence by sentence*. A claim is *supported*
when its content words overlap a context sentence above a threshold, with
numeric tokens required to match exactly (bag-of-words overlap alone cannot
tell "100" from "one million"). A claim is *contradicted* when it shares
the same facts but flips polarity (negation present on one side only).

Rubric: 5 = all claims supported, 4 = most, 3 = about half,
2 = mostly unsupported, 1 = contradicts the chunks.
"""

import re

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_WORD = re.compile(r"[a-z0-9']+")
_NEGATIONS = {"not", "no", "never", "none", "n't", "cannot", "can't", "won't",
              "don't", "doesn't", "isn't", "aren't", "wasn't", "weren't"}
_NUMBER_WORDS = {"one", "two", "three", "four", "five", "six", "seven",
                 "eight", "nine", "ten", "hundred", "thousand", "million",
                 "billion"}

_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "else", "when",
    "at", "by", "for", "with", "about", "into", "through", "during",
    "of", "to", "in", "on", "is", "are", "was", "were", "be", "been",
    "being", "it", "its", "this", "that", "these", "those", "as", "from",
    "you", "your", "we", "our", "they", "their", "he", "she", "his", "her",
    "i", "my", "me", "do", "does", "did", "has", "have", "had", "will",
    "would", "can", "could", "should", "there", "here", "all", "any",
    "each", "such", "up", "out", "over", "under", "between",
}


def tokens(text):
    return _WORD.findall(text.lower())


def content_words(text):
    return {w for w in tokens(text) if w not in _STOPWORDS and len(w) > 2}


def number_tokens(text):
    return {w for w in tokens(text)
            if w.isdigit() or w in _NUMBER_WORDS}


def has_negation(text):
    return any(n in text.lower() for n in _NEGATIONS)


def split_claims(answer):
    return [s.strip() for s in _SENTENCE_SPLIT.split(answer.strip()) if s.strip()]


def judge(answer, chunks, threshold=0.5):
    """Score the answer 1-5 and return per-claim verdicts."""
    context = []
    for chunk in chunks:
        for sent in split_claims(chunk["text"]):
            context.append({
                "text": sent,
                "words": content_words(sent),
                "numbers": number_tokens(sent),
                "negated": has_negation(sent),
            })

    verdicts = []
    for claim in split_claims(answer):
        words = content_words(claim)
        if not words:
            verdicts.append({"claim": claim, "verdict": "empty", "overlap": 0.0})
            continue
        claim_numbers = number_tokens(claim)
        claim_neg = has_negation(claim)
        best, best_ratio = None, 0.0
        for sent in context:
            if not sent["words"]:
                continue
            ratio = len(words & sent["words"]) / len(words)
            if ratio > best_ratio:
                best, best_ratio = sent, ratio
        if best is None:
            verdict = "unsupported"
        elif claim_numbers and not claim_numbers <= best["numbers"]:
            # numeric claim the evidence doesn't contain -> not grounded
            verdict = "unsupported"
        elif claim_neg and not best["negated"] and best_ratio >= 0.4:
            # negated claim about facts the evidence states positively
            verdict = "contradicted"
        elif best_ratio >= threshold:
            verdict = "supported"
        else:
            verdict = "unsupported"
        verdicts.append({"claim": claim, "verdict": verdict,
                         "overlap": round(best_ratio, 3)})

    counts = {v: sum(1 for x in verdicts if x["verdict"] == v)
              for v in ("supported", "unsupported", "contradicted")}
    n = len(verdicts) or 1
    if counts["contradicted"]:
        score = 1
    else:
        frac = counts["supported"] / n
        score = 5 if frac == 1.0 else 4 if frac >= 0.75 else 3 if frac >= 0.5 else 2
    return {"score": score, "claims": len(verdicts), **counts,
            "verdicts": verdicts}
