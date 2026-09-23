# Customers

The Customer object stores reusable payer details: email, name, and saved payment methods. Create one with `POST /v1/customers`.

Attach payment methods with `POST /v1/customers/{id}/payment_methods`. A customer can have up to 10 saved payment methods; mark one as default for subscriptions.

Deleting a customer is soft-delete: the record is retained for 90 days for compliance, then purged. Customer metadata supports up to 20 key-value pairs, each key max 40 characters.
