from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
from math import ceil
from zoneinfo import ZoneInfo

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models import Transaction


@dataclass(frozen=True)
class TransactionFilters:
    search: str | None = None
    categories: tuple[str, ...] = ()
    statuses: tuple[str, ...] = ()
    date_from: date | None = None
    date_to: date | None = None
    min_amount: Decimal | None = None
    max_amount: Decimal | None = None


def split_values(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(part.strip() for part in value.split(",") if part.strip())


def _date_boundary(value: date, end: bool) -> datetime:
    local = datetime.combine(value, time.max if end else time.min, tzinfo=ZoneInfo("Asia/Kolkata"))
    return local.astimezone(ZoneInfo("UTC"))


def apply_transaction_filters(statement: Select, user_id, filters: TransactionFilters) -> Select:
    statement = statement.where(Transaction.user_id == user_id)
    if filters.search:
        statement = statement.where(func.lower(Transaction.merchant).contains(filters.search.lower()))
    if filters.categories:
        statement = statement.where(Transaction.category.in_(filters.categories))
    if filters.statuses:
        statement = statement.where(Transaction.status.in_(tuple(status.upper() for status in filters.statuses)))
    if filters.date_from:
        statement = statement.where(Transaction.occurred_at >= _date_boundary(filters.date_from, False))
    if filters.date_to:
        statement = statement.where(Transaction.occurred_at <= _date_boundary(filters.date_to, True))
    if filters.min_amount is not None:
        statement = statement.where(Transaction.amount >= filters.min_amount)
    if filters.max_amount is not None:
        statement = statement.where(Transaction.amount <= filters.max_amount)
    return statement


def list_transactions(
    session: Session,
    user_id,
    filters: TransactionFilters,
    page: int,
    page_size: int,
    sort_by: str,
    sort_order: str,
):
    base = apply_transaction_filters(select(Transaction), user_id, filters)
    total = session.scalar(select(func.count()).select_from(base.subquery())) or 0
    sort_column = Transaction.occurred_at if sort_by == "date" else Transaction.amount
    order = sort_column.asc() if sort_order == "asc" else sort_column.desc()
    items = session.scalars(base.order_by(order, Transaction.id.asc()).offset((page - 1) * page_size).limit(page_size)).all()
    return items, total, ceil(total / page_size) if total else 0


def analytics(session: Session, user_id, filters: TransactionFilters):
    successful = apply_transaction_filters(select(Transaction), user_id, filters).where(Transaction.status == "SUCCESS")
    category_rows = session.execute(
        successful.with_only_columns(Transaction.category, func.coalesce(func.sum(Transaction.amount), 0).label("amount"))
        .group_by(Transaction.category)
        .order_by(func.sum(Transaction.amount).desc())
    ).all()
    month_label = func.to_char(func.date_trunc("month", Transaction.occurred_at), "YYYY-MM")
    monthly_rows = session.execute(
        successful.with_only_columns(month_label.label("month"), func.coalesce(func.sum(Transaction.amount), 0).label("amount"))
        .group_by(month_label)
        .order_by(month_label)
    ).all()
    return category_rows, monthly_rows

