# Rate Limits

NimbusPay enforces per-key rate limits. Default quota: 100 requests per second and 10,000 requests per day on standard plans. Enterprise plans raise the per-second limit to 500.

When you exceed the limit the API returns HTTP 429 with a `Retry-After` header (seconds). Implement exponential backoff with jitter; do not hammer the endpoint.

Check current usage via the `X-RateLimit-Remaining` and `X-RateLimit-Reset` response headers on every call. Burst capacity allows short spikes of 2x the per-second quota for up to 10 seconds.
