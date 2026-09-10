import logging

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from utilities.auth import create_access_token
from utilities.hash_password import hash_password, verify_password
from utilities.model import Role, UserModel
from utilities.roles import RoleName
from utilities.schema import LoginRequest, UserCreate

logger = logging.getLogger(__name__)


def signup_user(db: Session, user_in: UserCreate) -> UserModel:
    default_role = db.query(Role).filter(Role.role == RoleName.USER.value).first()
    if default_role is None:
        logger.error("Default role '%s' is not seeded in the database", RoleName.USER.value)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Signup is temporarily unavailable",
        )

    db_user = UserModel(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        role_id=default_role.id,
    )

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

    return db_user


def authenticate_user(db: Session, data: LoginRequest) -> str:
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

    return create_access_token(str(user.id))
