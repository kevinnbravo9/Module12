import pytest
from pydantic import ValidationError

from app.models import Calculation, User
from app.schemas import CalculationCreate, CalculationRead


def test_create_with_a_and_b():
    calc = CalculationCreate(
        user_id=1, a=10, b=5, type="addition"
    )
    assert calc.inputs == [10, 5]
    assert calc.a == 10
    assert calc.b == 5


def test_create_with_inputs():
    calc = CalculationCreate(
        user_id=1, inputs=[10, 5], type="addition"
    )
    assert calc.a == 10
    assert calc.b == 5


def test_division_by_zero_with_a_and_b():
    with pytest.raises(ValidationError):
        CalculationCreate(
            user_id=1, a=10, b=0, type="division"
        )


def test_mismatched_operands():
    with pytest.raises(ValidationError):
        CalculationCreate(
            user_id=1,
            a=10,
            b=5,
            inputs=[20, 5],
            type="addition",
        )


def test_read_contains_a_and_b():
    from datetime import datetime, timezone

    calc = CalculationRead(
        id=1,
        user_id=1,
        type="addition",
        inputs=[10, 5],
        result=15,
        created_at=datetime.now(timezone.utc),
    )
    assert calc.a == 10
    assert calc.b == 5


def test_database_stores_a_and_b(db_session):
    user = User(
        username="operands_test",
        email="operands_test@example.com",
        password_hash="test_hash",
    )
    db_session.add(user)
    db_session.flush()

    calc = Calculation.create(
        "addition", user_id=user.id, inputs=[10, 5]
    )
    calc.result = calc.get_result()

    db_session.add(calc)
    db_session.commit()
    db_session.expire_all()

    saved = db_session.get(Calculation, calc.id)

    assert saved is not None
    assert saved.a == 10
    assert saved.b == 5
    assert saved.inputs == [10, 5]
    assert saved.result == 15
