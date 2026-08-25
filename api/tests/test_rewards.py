from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models import Reward, User
from app.services import DEMO_EMAIL, redeem_reward


def make_session():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    session.add(User(email=DEMO_EMAIL, display_name="Demo", coin_balance=500))
    session.add(Reward(id="reward", title="Reward", description="Test", coin_cost=250, accent="teal"))
    session.commit()
    return session


def test_redemption_is_idempotent_and_debits_once():
    session = make_session()
    redemption, balance, replayed = redeem_reward(session, "reward", "12345678")
    assert balance == 250
    assert not replayed
    replay, replay_balance, replayed = redeem_reward(session, "reward", "12345678")
    assert replay.id == redemption.id
    assert replay_balance == 250
    assert replayed


def test_redemption_rejects_insufficient_balance():
    from fastapi import HTTPException

    session = make_session()
    session.query(User).filter_by(email=DEMO_EMAIL).update({"coin_balance": 5})
    session.commit()
    try:
        redeem_reward(session, "reward", "abcdefgh")
    except HTTPException as error:
        assert error.status_code == 409
    else:
        raise AssertionError("Expected insufficient-balance error")


def test_redemption_rejects_unknown_reward():
    from fastapi import HTTPException

    session = make_session()
    try:
        redeem_reward(session, "missing", "abcdefgh")
    except HTTPException as error:
        assert error.status_code == 404
    else:
        raise AssertionError("Expected unknown-reward error")
