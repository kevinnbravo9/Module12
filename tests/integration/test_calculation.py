
import pytest

from app.models import (
    Calculation,
    Addition,
    Subtraction,
    Multiplication,
    Division,
)


@pytest.mark.parametrize(
    "operation,inputs,expected",
    [
        ("addition", [10, 5], 15),
        ("subtraction", [10, 5], 5),
        ("multiplication", [10, 5], 50),
        ("division", [10, 5], 2),
    ],
)
def test_calculation_operations(operation, inputs, expected):
    calc = Calculation.create(operation, user_id=1, inputs=inputs)
    assert calc.get_result() == pytest.approx(expected)


@pytest.mark.parametrize(
    "operation,expected_class",
    [
        ("addition", Addition),
        ("subtraction", Subtraction),
        ("multiplication", Multiplication),
        ("division", Division),
    ],
)
def test_factory_pattern(operation, expected_class):
    calc = Calculation.create(operation, user_id=1, inputs=[10, 2])
    assert isinstance(calc, expected_class)


def test_invalid_calculation_type():
    with pytest.raises(ValueError):
        Calculation.create("power", user_id=1, inputs=[10, 2])


def test_division_by_zero():
    calc = Calculation.create("division", user_id=1, inputs=[10, 0])
    with pytest.raises(ValueError):
        calc.get_result()


def test_calculation_requires_two_numbers():
    calc = Calculation.create("addition", user_id=1, inputs=[10])
    with pytest.raises(ValueError):
        calc.get_result()


def test_calculation_database(db_session):
    from app.models import User

    user = User(
        username="calculation_test",
        email="calculation_test@example.com",
        password_hash="test_hash",
    )
    db_session.add(user)
    db_session.flush()

    calc = Calculation.create(
        "addition",
        user_id=user.id,
        inputs=[10, 5],
    )
    calc.result = calc.get_result()

    db_session.add(calc)
    db_session.commit()

    saved = db_session.get(Calculation, calc.id)

    assert saved is not None
    assert isinstance(saved, Addition)
    assert saved.inputs == [10, 5]
    assert saved.result == 15
    assert saved.user_id == user.id
