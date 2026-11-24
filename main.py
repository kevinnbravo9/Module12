import logging

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from pydantic import BaseModel

from app.operations import add, subtract, multiply, divide


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FastAPI Calculator")

templates = Jinja2Templates(directory="templates")


class Numbers(BaseModel):
    a: float
    b: float


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.post("/add")
async def add_numbers(numbers: Numbers):
    logger.info(f"Adding {numbers.a} and {numbers.b}")
    return {"result": add(numbers.a, numbers.b)}


@app.post("/subtract")
async def subtract_numbers(numbers: Numbers):
    logger.info(f"Subtracting {numbers.b} from {numbers.a}")
    return {"result": subtract(numbers.a, numbers.b)}


@app.post("/multiply")
async def multiply_numbers(numbers: Numbers):
    logger.info(f"Multiplying {numbers.a} and {numbers.b}")
    return {"result": multiply(numbers.a, numbers.b)}


@app.post("/divide")
async def divide_numbers(numbers: Numbers):
    logger.info(f"Dividing {numbers.a} by {numbers.b}")

    try:
        result = divide(numbers.a, numbers.b)
        return {"result": result}
    except ValueError as error:
        logger.error(f"Calculation error: {error}")
        raise HTTPException(status_code=400, detail=str(error))

# Module 12: User registration and authentication

from fastapi import Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import create_access_token
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserRead, UserLogin, TokenResponse
from app.security import verify_password
from app.user_service import create_user


@app.post(
    "/users/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Users"],
)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        return create_user(db, user_data)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.post(
    "/users/login",
    response_model=TokenResponse,
    tags=["Users"],
)
def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        (User.username == user_data.username)
        | (User.email == user_data.username)
    ).first()

    if user is None or not user.password_hash or not verify_password(
        user_data.password, user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    return TokenResponse(
        access_token=create_access_token(user.id),
        token_type="bearer",
    )


@app.post("/users/token", tags=["Users"])
def login_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(
        User.username == form_data.username
    ).first()

    if user is None or not user.password_hash or not verify_password(
        form_data.password, user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }


# Module 12: Calculation BREAD endpoints
from app.calculation_routes import router as calculation_router

app.include_router(calculation_router)
