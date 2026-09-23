# Webhooks

NimbusPay sends webhook events as JSON POST requests to your registered endpoint. Configure endpoints under Settings > Webhooks; up to 16 endpoints per account.

Verify authenticity by checking the `Nimbus-Signature` header: compute HMAC-SHA256 of the raw request body with your webhook secret and compare in constant time.

Your endpoint must respond with HTTP 200 within 5 seconds. Failed deliveries retry with exponential backoff: after 1 minute, 5 minutes, 30 minutes, then hourly for up to 72 hours. Common events: `payment.succeeded`, `payment.failed`, `refund.created`, `payout.paid`.
