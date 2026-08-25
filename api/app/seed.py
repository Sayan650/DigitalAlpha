"""Create the schema and load the supplied transaction JSON deterministically."""
import argparse
import json
import re
import uuid
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from zoneinfo import ZoneInfo

from dateutil import parser
from sqlalchemy import delete

from app.config import get_settings
from app.db import Base, SessionLocal, engine
from app.models import CoinLedger, Redemption, Reward, Transaction, User
from app.services import DEMO_EMAIL

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "transactions_DA.json"
REWARDS = (
    ("cashback-25", "₹25 cashback", "Instant credit applied to your Coinwise account.", 250, "teal"),
    ("amazon-50", "₹50 Amazon voucher", "A digital Amazon gift voucher.", 500, "violet"),
    ("swiggy-75", "₹75 Swiggy voucher", "A food delivery reward for your next order.", 750, "orange"),
    ("uber-100", "₹100 Uber credit", "Ride credit for your next trip.", 1000, "blue"),
    ("flipkart-150", "₹150 Flipkart voucher", "A shopping voucher delivered in-app.", 1500, "pink"),
)


def normalize_timestamp(value) -> datetime:
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc)
    text = str(value).strip()
    if "/" in text:
        parsed = parser.parse(text, dayfirst=True)
    elif re.match(r"^\d{4}-\d{2}-\d{2}", text):
        parsed = parser.isoparse(text)
    else:
        parsed = parser.parse(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=ZoneInfo(get_settings().app_timezone))
    return parsed.astimezone(timezone.utc)


def normalize_row(row: dict, user_id: uuid.UUID) -> tuple[Transaction, int]:
    amount = Decimal(str(row["amount"])).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    category = str(row.get("category") or "").strip() or "Uncategorized"
    status = str(row["status"]).strip().upper()
    transaction = Transaction(
        id=uuid.uuid4(),
        user_id=user_id,
        source_transaction_id=str(row["id"]),
        occurred_at=normalize_timestamp(row["timestamp"]),
        merchant=str(row["merchant"]).strip(),
        category=category,
        amount=amount,
        currency=str(row["currency"]).strip().upper(),
        status=status,
        payment_method=str(row["payment_method"]).strip(),
        raw_timestamp=str(row["timestamp"]),
    )
    earned = min(int(amount // Decimal("100")), 100) if status == "SUCCESS" and amount > 0 else 0
    return transaction, earned


def seed(data_path: Path, reset: bool = False) -> dict[str, int]:
    if not data_path.exists():
        raise FileNotFoundError(f"Transaction data not found: {data_path}")
    if reset:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    rows = json.loads(data_path.read_text(encoding="utf-8"))

    with SessionLocal() as session:
        if reset:
            # Kept for clarity if this seed is changed to avoid dropping schema in future.
            session.execute(delete(CoinLedger))
            session.execute(delete(Redemption))
            session.execute(delete(Transaction))
            session.execute(delete(Reward))
            session.execute(delete(User))
        existing = session.query(Transaction).count()
        if existing:
            return {"transactions": existing, "coins": session.query(CoinLedger).count()}

        user = User(id=uuid.uuid4(), email=DEMO_EMAIL, display_name="Aarav Shah", coin_balance=0)
        session.add(user)
        session.add_all(Reward(id=reward_id, title=title, description=description, coin_cost=cost, accent=accent) for reward_id, title, description, cost, accent in REWARDS)

        total_coins = 0
        for index in range(0, len(rows), 500):
            batch = []
            ledger = []
            for row in rows[index : index + 500]:
                transaction, earned = normalize_row(row, user.id)
                batch.append(transaction)
                if earned:
                    ledger.append(CoinLedger(user_id=user.id, transaction_id=transaction.id, delta=earned, kind="TRANSACTION_EARNED"))
                    total_coins += earned
            session.add_all(batch)
            session.add_all(ledger)
            session.flush()
        user.coin_balance = total_coins
        session.commit()
        return {"transactions": len(rows), "coins": total_coins}


def main() -> None:
    command = argparse.ArgumentParser()
    command.add_argument("--data", type=Path, default=DATA_PATH)
    command.add_argument("--reset", action="store_true")
    args = command.parse_args()
    summary = seed(args.data, reset=args.reset)
    print(f"Seeded {summary['transactions']} transactions and {summary['coins']} coins.")


if __name__ == "__main__":
    main()

