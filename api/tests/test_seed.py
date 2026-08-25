import json
from pathlib import Path
from uuid import uuid4

from app.seed import normalize_row, normalize_timestamp


def test_normalizes_each_timestamp_shape_and_amount():
    user_id = uuid4()
    cases = [
        ("2025-10-03T21:03:27Z", "2025-10-03T21:03:27+00:00"),
        (1768265109000, "2026-01-13T00:45:09+00:00"),
        ("21/08/2025 09:14:08", "2025-08-21T03:44:08+00:00"),
        ("2026-04-29", "2026-04-28T18:30:00+00:00"),
    ]
    for timestamp, expected in cases:
        row = {
            "id": "source-id", "timestamp": timestamp, "merchant": "Store", "category": None,
            "amount": "912.62", "currency": "inr", "status": "success", "payment_method": "UPI",
        }
        transaction, earned = normalize_row(row, user_id)
        assert transaction.occurred_at.isoformat() == expected
        assert transaction.category == "Uncategorized"
        assert transaction.status == "SUCCESS"
        assert str(transaction.amount) == "912.62"
        assert earned == 9


def test_source_data_is_fully_normalizable():
    data_path = Path(__file__).resolve().parents[1] / "data" / "transactions_DA.json"
    rows = json.loads(data_path.read_text(encoding="utf-8"))
    normalized = [normalize_row(row, uuid4()) for row in rows]
    assert len(normalized) == 10_000
    assert sum(transaction.category == "Uncategorized" for transaction, _ in normalized) == 200
    assert sum(earned > 0 for _, earned in normalized) > 0
    assert max(earned for _, earned in normalized) == 100
