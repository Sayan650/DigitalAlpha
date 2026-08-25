import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CoinLedger, Redemption, Reward, User


DEMO_EMAIL = "demo@coinwise.app"


def get_demo_user(session: Session) -> User:
    user = session.scalar(select(User).where(User.email == DEMO_EMAIL))
    if not user:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Demo data has not been seeded.")
    return user


def redeem_reward(session: Session, reward_id: str, idempotency_key: str):
    existing = session.scalar(
        select(Redemption).where(Redemption.user_id == get_demo_user(session).id, Redemption.idempotency_key == idempotency_key)
    )
    if existing:
        return existing, get_demo_user(session).coin_balance, True

    reward = session.get(Reward, reward_id)
    if not reward or not reward.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reward does not exist.")

    user = session.scalar(select(User).where(User.email == DEMO_EMAIL).with_for_update())
    if not user:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Demo data has not been seeded.")
    if user.coin_balance < reward.coin_cost:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Insufficient coin balance for this reward.")

    redemption = Redemption(
        id=uuid.uuid4(),
        user_id=user.id,
        reward_id=reward.id,
        coins_spent=reward.coin_cost,
        idempotency_key=idempotency_key,
    )
    user.coin_balance -= reward.coin_cost
    session.add(redemption)
    session.flush()
    session.add(CoinLedger(user_id=user.id, redemption_id=redemption.id, delta=-reward.coin_cost, kind="REDEMPTION"))
    session.commit()
    return redemption, user.coin_balance, False

