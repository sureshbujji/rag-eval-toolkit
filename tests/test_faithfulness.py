from src.faithfulness import judge

CHUNKS = [
    {"id": "c1", "doc_id": "webhooks",
     "text": "Verify webhooks by computing HMAC-SHA256 of the raw request body "
             "with your webhook secret and compare the Nimbus-Signature header "
             "in constant time."},
    {"id": "c2", "doc_id": "webhooks",
     "text": "Your endpoint must respond with HTTP 200 within 5 seconds."},
]


def test_grounded_answer_scores_5():
    answer = ("Verify webhooks by computing HMAC-SHA256 of the raw request body "
              "with your webhook secret. Compare the Nimbus-Signature header "
              "in constant time.")
    result = judge(answer, CHUNKS)
    assert result["score"] == 5
    assert result["supported"] == result["claims"]


def test_ungrounded_answer_scores_low():
    answer = ("Webhooks use RSA-2048 signatures verified inside the merchant "
              "dashboard. No response code is required from your endpoint.")
    result = judge(answer, CHUNKS)
    assert result["score"] <= 2


def test_contradiction_scores_1():
    answer = "You do not need to verify webhook signatures at all."
    result = judge(answer, CHUNKS)
    assert result["score"] == 1
    assert result["contradicted"] >= 1
