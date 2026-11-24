
import pytest
from pydantic import ValidationError

from app.schemas import CalculationCreate, CalculationType


@pytest.mark.parametrize(
    "operation",
    ["addition", "subtraction", "multiplication", "division"],
)
def test_valid_calculation_types(operation):
    calc = CalculationCreate(
        type=operation,
        inputs=[10, 2],
        user_id=1,
    )
    assert calc.type.value == operation


def test_calculation_type_case_insensitive():
    calc = CalculationCreate(
        type="ADDITION",
        inputs=[10, 2],
        user_id=1,
    )
    assert calc.type == CalculationType.ADDITION


def test_invalid_calculation_type():
    with pytest.raises(ValidationError):
        CalculationCreate(
            type="power",
            inputs=[10, 2],
            user_id=1,
        )


def test_division_by_zero():
    with pytest.raises(ValidationError):
        CalculationCreate(
            type="division",
            inputs=[10, 0],
            user_id=1,
        )


def test_insufficient_inputs():
    with pytest.raises(ValidationError):
        CalculationCreate(
            type="addition",
            inputs=[10],
            user_id=1,
        )


def test_invalid_user_id():
    with pytest.raises(ValidationError):
        CalculationCreate(
            type="addition",
            inputs=[10, 2],
            user_id=0,
        )


def test_invalid_input_type():
    with pytest.raises(ValidationError):
        CalculationCreate(
            type="addition",
            inputs="10,2",
            user_id=1,
        )


def test_non_finite_input():
    with pytest.raises(ValidationError):
        CalculationCreate(
            type="addition",
            inputs=[float("inf"), 2],
            user_id=1,
        )


from app.schemas import CalculationUpdate, CalculationResponse
from datetime import datetime, timezone


def test_calculation_update_valid():
    calc = CalculationUpdate(inputs=[42, 7])
    assert calc.inputs == [42, 7]


def test_calculation_update_empty():
    calc = CalculationUpdate()
    assert calc.inputs is None


def test_calculation_update_invalid_inputs():
    with pytest.raises(ValidationError):
        CalculationUpdate(inputs=[5])


def test_calculation_update_non_finite():
    with pytest.raises(ValidationError):
        CalculationUpdate(inputs=[float("inf"), 2])



def test_calculation_response_valid():
    now = datetime.now(timezone.utc)

    calc = CalculationResponse(
        id=1,
        user_id=1,
        type="addition",
        inputs=[10, 5],
        result=15.0,
        created_at=now,
        updated_at=now,
    )

    assert calc.result == 15.0
    assert calc.updated_at == now


def test_calculation_response_missing_result():
    with pytest.raises(ValidationError):
        CalculationResponse(
            id=1,
            user_id=1,
            type="addition",
            inputs=[10, 5],
            created_at=datetime.now(timezone.utc),
        )
