# Product assumptions

- This submission has one seeded demo account and no authentication.
- INR is the only currency. Failed and pending rows remain visible but do not contribute to analytics or coins.
- Negative successful amounts are refunds: they reduce monthly/category net spend and earn zero coins.
- Each historic successful, positive transaction earns `floor(amount / 100)` coins, capped at 100. Repeated source IDs are retained as distinct imported records.
- Missing categories are shown as `Uncategorized`. Slash dates are interpreted as `DD/MM/YYYY`; timezone-less values are Asia/Kolkata.
- A reward redemption records an in-app claim only; it does not issue a real voucher.

