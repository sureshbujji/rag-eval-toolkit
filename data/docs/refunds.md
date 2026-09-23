# Refunds

Issue a refund with `POST /v1/refunds`, passing `payment_id` and optionally `amount` for a partial refund. Full refunds are the default when amount is omitted.

Refunds take 5-10 business days to reach the customer's statement. A refund can only be issued on a `succeeded` payment and within 180 days of the original charge.

Refunded amounts are netted against your next payout. The `refund.reason` field accepts `duplicate`, `fraudulent`, or `requested_by_customer`. Each refund generates a `refund.created` webhook event.
