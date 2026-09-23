# Creating Payments

Create a charge with `POST /v1/payments`. Required fields: `amount` (integer cents), `currency` (ISO-4217, e.g. `usd`), and a `payment_method` token.

A payment moves through states: `created` -> `processing` -> `succeeded` (or `failed`). Use idempotency keys via the `Idempotency-Key` header to safely retry requests; keys are stored for 24 hours.

Partial captures are supported: authorize now and capture up to 115% of the authorized amount within 7 days. After 7 days the authorization expires automatically and funds are released.
