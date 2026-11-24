from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Calculation, User
from app.schemas import (
    CalculationBase,
    CalculationResponse,
    CalculationUpdate,
)

router = APIRouter(prefix="/calculations", tags=["Calculations"])


def find_calculation(
    calculation_id: int,
    db: Session,
    user: User,
) -> Calculation:
    calculation = db.scalar(
        select(Calculation).where(
            Calculation.id == calculation_id,
            Calculation.user_id == user.id,
        )
    )
    if calculation is None:
        raise HTTPException(
            status_code=404,
            detail="Calculation not found",
        )
    return calculation


@router.post(
    "",
    response_model=CalculationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_calculation(
    data: CalculationBase,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    calculation = Calculation.create(
        calculation_type=data.type.value,
        user_id=user.id,
        inputs=data.inputs,
    )
    calculation.result = calculation.get_result()

    db.add(calculation)
    db.commit()
    db.refresh(calculation)
    return calculation


@router.get("", response_model=list[CalculationResponse])
def list_calculations(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return db.scalars(
        select(Calculation)
        .where(Calculation.user_id == user.id)
        .order_by(Calculation.id)
    ).all()


@router.get("/{calculation_id}", response_model=CalculationResponse)
def read_calculation(
    calculation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return find_calculation(calculation_id, db, user)


@router.put("/{calculation_id}", response_model=CalculationResponse)
def update_calculation(
    calculation_id: int,
    data: CalculationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    calculation = find_calculation(calculation_id, db, user)

    if data.inputs is None:
        raise HTTPException(
            status_code=422,
            detail="Inputs are required for an update",
        )

    if calculation.type == "division" and any(
        value == 0 for value in data.inputs[1:]
    ):
        raise HTTPException(
            status_code=422,
            detail="Cannot divide by zero",
        )

    original_inputs = calculation.inputs
    calculation.inputs = data.inputs

    try:
        result = calculation.get_result()
    except (ValueError, ZeroDivisionError) as error:
        calculation.inputs = original_inputs
        raise HTTPException(status_code=422, detail=str(error))

    calculation.a = data.inputs[0]
    calculation.b = data.inputs[1]
    calculation.result = result

    db.commit()
    db.refresh(calculation)
    return calculation


@router.delete("/{calculation_id}", status_code=204)
def delete_calculation(
    calculation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    calculation = find_calculation(calculation_id, db, user)
    db.delete(calculation)
    db.commit()
