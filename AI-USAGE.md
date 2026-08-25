# AI usage

I used an AI coding assistant to help scaffold components, review API shapes, and generate initial test cases. I reviewed and edited all resulting code.

## Discarded or corrected output

1. An early generated seed approach used the source transaction ID as a primary key. I discarded it because the supplied data contains duplicate IDs; the implementation uses an internal UUID and keeps the source ID as provenance.
2. An initial analytics query included pending and failed payments. I corrected it so charts contain only successful transactions and negative successful amounts remain refunds.

