# Payouts

Payouts move your NimbusPay balance to your bank account. Default schedule is daily automatic; you can switch to weekly or manual in the dashboard.

The minimum payout amount is $1.00 (100 cents). Payouts arrive in 2 business days for US banks and 3-5 business days internationally. Each payout has a `payout_id` and emits a `payout.paid` webhook.

Failed payouts (wrong account number, closed account) return funds to your NimbusPay balance within 5 business days and trigger a `payout.failed` event.
