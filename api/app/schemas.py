from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_transaction_id: str
    occurred_at: datetime
    merchant: str
    category: str
    amount: Decimal
    currency: str
    status: str
    payment_method: str
    raw_timestamp: str


class TransactionPage(BaseModel):
    items: list[TransactionOut]
    total: int
    page: int
    page_size: int
    total_pages: int


class CategorySpend(BaseModel):
    category: str
    amount: Decimal


class MonthlySpend(BaseModel):
    month: str
    amount: Decimal


class AnalyticsOut(BaseModel):
    by_category: list[CategorySpend]
    by_month: list[MonthlySpend]


class BalanceOut(BaseModel):
    balance: int


class RewardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    coin_cost: int
    accent: str


class RedeemIn(BaseModel):
    reward_id: str = Field(min_length=1, max_length=64)
    idempotency_key: str = Field(min_length=8, max_length=100)


class RedemptionOut(BaseModel):
    redemption_id: UUID
    reward_id: str
    balance: int
    already_processed: bool = False

