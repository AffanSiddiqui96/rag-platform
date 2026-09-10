
import logging

from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from utilities.auth import create_access_token
from utilities.hash_password import hash_password, verify_password
from utilities.model import Role, UserModel
from utilities.roles import RoleName
from utilities.schema import UserCreate, UserResponse, LoginRequest, LoginResponse



router = APIRouter(
    prefix="/user",
    tags=["users"],
)

logger = logging.getLogger(__name__)


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    default_role = db.query(Role).filter(Role.role == RoleName.USER.value).first()
    if default_role is None:
        logger.error("Default role '%s' is not seeded in the database", RoleName.USER.value)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Signup is temporarily unavailable",
        )

    # 1. Pydantic validates 'user_in' automatically
    db_user = UserModel(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        role_id=default_role.id,
    )

    # 2. Save to database
    try:
        db.add(db_user)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with that username or email already exists",
        )
    db.refresh(db_user)

    # 3. Returns db_user, formatted automatically via UserResponse schema
    return db_user


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == data.email).first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated",
        )

    access_token = create_access_token(str(user.id))

    return LoginResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse)
def get_profile(current_user: UserModel = Depends(get_current_user)):
    return current_user
