from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Float, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )

    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )

    password_hash: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    calculations: Mapped[list["Calculation"]] = relationship(
        "Calculation",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Calculation(Base):
    __tablename__ = "calculations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    inputs: Mapped[list] = mapped_column(JSON, nullable=False)

    a: Mapped[float | None] = mapped_column(Float, nullable=True)
    b: Mapped[float | None] = mapped_column(Float, nullable=True)


    result: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


    user: Mapped["User"] = relationship(
        "User",
        back_populates="calculations",
    )

    __mapper_args__ = {
        "polymorphic_on": "type",
        "polymorphic_identity": "calculation",
    }



    @classmethod
    def create(cls, calculation_type: str, user_id: int, inputs: list):
        calculation_classes = {
            "addition": Addition,
            "subtraction": Subtraction,
            "multiplication": Multiplication,
            "division": Division,
        }

        calculation_class = calculation_classes.get(calculation_type.lower())

        if calculation_class is None:
            raise ValueError(f"Unsupported calculation type: {calculation_type}")


        return calculation_class(
            user_id=user_id,
            inputs=inputs,
            a=inputs[0] if isinstance(inputs, list) and len(inputs) > 0 else None,
            b=inputs[1] if isinstance(inputs, list) and len(inputs) > 1 else None,
        )



class Addition(Calculation):
    __mapper_args__ = {"polymorphic_identity": "addition"}

    def get_result(self):
        if not isinstance(self.inputs, list):
            raise ValueError("Inputs must be a list of numbers.")

        if len(self.inputs) < 2:
            raise ValueError("Inputs must be a list with at least two numbers.")
        return sum(self.inputs)


class Subtraction(Calculation):
    __mapper_args__ = {"polymorphic_identity": "subtraction"}

    def get_result(self):
        if not isinstance(self.inputs, list):
            raise ValueError("Inputs must be a list of numbers.")

        if len(self.inputs) < 2:
            raise ValueError("Inputs must be a list with at least two numbers.")

        result = self.inputs[0]
        for value in self.inputs[1:]:
            result -= value
        return result

class Multiplication(Calculation):
    __mapper_args__ = {"polymorphic_identity": "multiplication"}

    def get_result(self):
        if not isinstance(self.inputs, list):
            raise ValueError("Inputs must be a list of numbers.")

        if len(self.inputs) < 2:
            raise ValueError("Inputs must be a list with at least two numbers.")

        result = 1
        for value in self.inputs:
            result *= value

        return result

class Division(Calculation):
    __mapper_args__ = {"polymorphic_identity": "division"}

    def get_result(self):
        if not isinstance(self.inputs, list):
            raise ValueError("Inputs must be a list of numbers.")

        if len(self.inputs) < 2:
            raise ValueError("Inputs must be a list with at least two numbers.")

        result = self.inputs[0]
        for value in self.inputs[1:]:
            if value == 0:
                raise ValueError("Cannot divide by zero.")
            result /= value

        return result
