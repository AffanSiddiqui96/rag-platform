
import logging

from fastapi import Depends, status, APIRouter
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.services.user_service import authenticate_user, signup_user
from utilities.model import UserModel
from utilities.schema import UserCreate, UserResponse, LoginRequest, LoginResponse



router = APIRouter(
    prefix="/user",
    tags=["users"],
)

logger = logging.getLogger(__name__)


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    return signup_user(db, user_in)


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    access_token = authenticate_user(db, data)
    return LoginResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse)
def get_profile(current_user: UserModel = Depends(get_current_user)):
    return current_user
