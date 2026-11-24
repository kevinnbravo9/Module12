from enum import Enum
from math import isfinite
from pydantic import field_validator, model_validator

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    created_at: datetime


class CalculationType(str, Enum):
    ADDITION = "addition"
    SUBTRACTION = "subtraction"
    MULTIPLICATION = "multiplication"
    DIVISION = "division"


class CalculationBase(BaseModel):
    type: CalculationType
    inputs: list[float] = Field(min_length=2)

    @field_validator("type", mode="before")
    @classmethod
    def validate_type(cls, value):
        if not isinstance(value, str):
            raise ValueError("Calculation type must be a string")

        return value.lower()

    @field_validator("inputs")
    @classmethod
    def validate_numbers(cls, values):
        if not all(isfinite(value) for value in values):
            raise ValueError("Inputs must contain finite numbers")
        return values

    @model_validator(mode="after")
    def validate_inputs(self):
        if self.type == CalculationType.DIVISION:
            if any(value == 0 for value in self.inputs[1:]):
                raise ValueError("Cannot divide by zero")
        return self



class CalculationCreate(CalculationBase):
    user_id: int = Field(gt=0)
    a: float | None = None
    b: float | None = None

    @model_validator(mode="before")
    @classmethod
    def accept_two_operands(cls, data):
        if not isinstance(data, dict):
            return data

        data = data.copy()

        if "inputs" not in data and "a" in data and "b" in data:
            data["inputs"] = [data["a"], data["b"]]

        return data

    @model_validator(mode="after")
    def validate_operands(self):
        if self.a is not None and not isfinite(self.a):
            raise ValueError("Operand a must be finite")

        if self.b is not None and not isfinite(self.b):
            raise ValueError("Operand b must be finite")

        if self.a is not None and self.b is not None:
            if self.inputs[:2] != [self.a, self.b]:
                raise ValueError("Operands a and b must match inputs")

        self.a = self.inputs[0]
        self.b = self.inputs[1]

        return self



class CalculationRead(CalculationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    a: float | None = None
    b: float | None = None
    result: float | None = None
    created_at: datetime
    updated_at: datetime | None = None

    @model_validator(mode="after")
    def populate_operands(self):
        if self.a is None:
            self.a = self.inputs[0]

        if self.b is None:
            self.b = self.inputs[1]

        return self


class CalculationUpdate(BaseModel):
    inputs: list[float] | None = Field(default=None, min_length=2)

    @field_validator("inputs")
    @classmethod
    def validate_inputs(cls, values):
        if values is not None:
            if not all(isfinite(value) for value in values):
                raise ValueError("Inputs must contain finite numbers")
        return values



class CalculationResponse(CalculationRead):
    result: float
    updated_at: datetime


class UserLogin(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
