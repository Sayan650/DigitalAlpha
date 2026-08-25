from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models import Transaction, User
from app.repository import TransactionFilters, list_transactions


def test_server_filters_searches_and_sorts_transactions():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    user = User(email="filter@example.test", display_name="Filter", coin_balance=0)
    session.add(user)
    session.flush()
    session.add_all([
        Transaction(user_id=user.id, source_transaction_id="one", occurred_at=datetime(2026, 1, 1, tzinfo=timezone.utc), merchant="Metro Mart", category="Groceries", amount=Decimal("150"), currency="INR", status="SUCCESS", payment_method="UPI", raw_timestamp="2026-01-01"),
        Transaction(user_id=user.id, source_transaction_id="two", occurred_at=datetime(2026, 2, 1, tzinfo=timezone.utc), merchant="Metro Cafe", category="Food & Dining", amount=Decimal("800"), currency="INR", status="SUCCESS", payment_method="Credit Card", raw_timestamp="2026-02-01"),
        Transaction(user_id=user.id, source_transaction_id="three", occurred_at=datetime(2026, 3, 1, tzinfo=timezone.utc), merchant="Fuel Stop", category="Fuel", amount=Decimal("1200"), currency="INR", status="FAILED", payment_method="UPI", raw_timestamp="2026-03-01"),
    ])
    session.commit()

    items, total, pages = list_transactions(
        session, user.id, TransactionFilters(search="metro", statuses=("SUCCESS",)), 1, 50, "amount", "desc"
    )
    assert total == 2 and pages == 1
    assert [transaction.source_transaction_id for transaction in items] == ["two", "one"]

