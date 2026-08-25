# Technical decisions

- **Server pagination and filtering:** the API performs filtering, search, sorting, and aggregation so the browser never needs to manipulate 10,000 records for routine interactions.
- **Schema:** normalized transaction, reward, redemption, and ledger tables preserve auditability while keeping raw-source provenance in `source_transaction_id`.
- **State:** URL query parameters own table filters; React Query owns server state. This makes links shareable and avoids duplicated client state.
- **Rewards consistency:** a balance column is updated under a database row lock and every mutation has a corresponding immutable ledger entry. An idempotency key makes retrying a redemption safe.
- **Table:** it is built from semantic HTML/CSS rather than a table component library, per the assignment constraint.

