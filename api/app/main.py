from datetime import date
from decimal import Decimal

from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_session
from app.models import Reward
from app.repository import TransactionFilters, analytics, list_transactions, split_values
from app.schemas import AnalyticsOut, BalanceOut, RedeemIn, RedemptionOut, RewardOut, TransactionPage
from app.services import get_demo_user, redeem_reward

settings = get_settings()
app = FastAPI(title="Coinwise API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def filters_from_query(search, category, status, date_from, date_to, min_amount, max_amount):
    return TransactionFilters(
        search=search.strip() if search else None,
        categories=split_values(category),
        statuses=split_values(status),
        date_from=date_from,
        date_to=date_to,
        min_amount=min_amount,
        max_amount=max_amount,
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/v1/transactions", response_model=TransactionPage)
def transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    search: str | None = None,
    category: str | None = None,
    status: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    min_amount: Decimal | None = Query(None, ge=-1000000),
    max_amount: Decimal | None = Query(None, le=1000000000),
    sort_by: str = Query("date", pattern="^(date|amount)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    session: Session = Depends(get_session),
):
    if min_amount is not None and max_amount is not None and min_amount > max_amount:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="min_amount cannot exceed max_amount.")
    user = get_demo_user(session)
    items, total, total_pages = list_transactions(
        session, user.id, filters_from_query(search, category, status, date_from, date_to, min_amount, max_amount), page, page_size, sort_by, sort_order
    )
    return TransactionPage(items=items, total=total, page=page, page_size=page_size, total_pages=total_pages)


@app.get("/api/v1/analytics", response_model=AnalyticsOut)
def spend_analytics(
    search: str | None = None,
    category: str | None = None,
    status: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    min_amount: Decimal | None = None,
    max_amount: Decimal | None = None,
    session: Session = Depends(get_session),
):
    user = get_demo_user(session)
    category_rows, month_rows = analytics(session, user.id, filters_from_query(search, category, status, date_from, date_to, min_amount, max_amount))
    return AnalyticsOut(
        by_category=[{"category": row.category, "amount": row.amount} for row in category_rows],
        by_month=[{"month": row.month, "amount": row.amount} for row in month_rows],
    )


@app.get("/api/v1/balance", response_model=BalanceOut)
def balance(session: Session = Depends(get_session)):
    return BalanceOut(balance=get_demo_user(session).coin_balance)


@app.get("/api/v1/rewards", response_model=list[RewardOut])
def rewards(session: Session = Depends(get_session)):
    return session.scalars(select(Reward).where(Reward.is_active.is_(True)).order_by(Reward.coin_cost)).all()


@app.post("/api/v1/redeem", response_model=RedemptionOut)
def redeem(payload: RedeemIn, session: Session = Depends(get_session)):
    redemption, balance_after, already_processed = redeem_reward(session, payload.reward_id, payload.idempotency_key)
    return RedemptionOut(redemption_id=redemption.id, reward_id=redemption.reward_id, balance=balance_after, already_processed=already_processed)

