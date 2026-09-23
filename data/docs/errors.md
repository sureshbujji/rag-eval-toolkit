# Error Codes

All errors return a JSON body with `code`, `message`, and `request_id`. The HTTP status maps to the error class: 400 validation, 401 authentication, 402 payment declined, 404 not found, 429 rate limited.

Common codes: `card_declined` (the issuer refused the charge), `insufficient_funds`, `expired_card`, `invalid_api_key` (rotate your key in the dashboard), `idempotency_key_reused` (same key with different parameters).

Retry guidance: never retry 400s without fixing the request; retry 500s and 503s with backoff. Include the `request_id` when contacting support so they can trace the call.
