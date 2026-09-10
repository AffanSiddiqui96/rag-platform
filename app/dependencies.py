import logging

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from utilities.auth import decode_access_token
from utilities.model import UserModel

logger = logging.getLogger(__name__)

engine = create_engine(str(settings.DATABASE_URL))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# auto_error=False so a missing header surfaces as our own 401 payload
# instead of FastAPI's default "Not authenticated" response.
bearer_scheme = HTTPBearer(auto_error=False)

_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> UserModel:
    if credentials is None:
        raise _credentials_exception

    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.PyJWTError:
        raise _credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise _credentials_exception

    user = db.query(UserModel).filter(UserModel.id == int(user_id)).first()
    if user is None or not user.is_active:
        raise _credentials_exception

    return user


def require_role(*allowed_roles: str):
    """Dependency factory restricting an endpoint to the given role names."""

    def role_checker(current_user: UserModel = Depends(get_current_user)) -> UserModel:
        if current_user.role.role not in allowed_roles:
            logger.warning(
                "User id=%s role=%s denied access (requires one of %s)",
                current_user.id,
                current_user.role.role,
                allowed_roles,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return role_checker
