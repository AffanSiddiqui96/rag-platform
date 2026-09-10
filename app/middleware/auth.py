import logging

import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

from utilities.auth import decode_access_token

logger = logging.getLogger(__name__)

# Paths reachable without a token: health check, signup/login, and the
# interactive docs UI (no sensitive data, needed for a usable dev experience).
PUBLIC_PATHS = frozenset(
    {
        "/hello",
        "/hello/",
        "/hello/health",
        "/user/signup",
        "/user/login",
        "/docs",
        "/redoc",
        "/openapi.json",
    }
)


class AuthMiddleware(BaseHTTPMiddleware):
    """Secure-by-default gate: every request must carry a valid bearer token
    unless its path is explicitly whitelisted. This is a blanket check —
    it does not resolve or attach a user; endpoints that need the current
    user (or a specific role) still depend on `get_current_user` /
    `require_role` from app.dependencies for that.
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS" or request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return self._unauthorized("Missing bearer token")

        token = auth_header[len("Bearer ") :].strip()
        if not token:
            return self._unauthorized("Missing bearer token")

        try:
            decode_access_token(token)
        except jwt.ExpiredSignatureError:
            return self._unauthorized("Token has expired")
        except jwt.PyJWTError:
            logger.info("Rejected request to %s: invalid token", request.url.path)
            return self._unauthorized("Invalid token")

        return await call_next(request)

    @staticmethod
    def _unauthorized(message: str) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={"error": {"status_code": 401, "message": message}},
            headers={"WWW-Authenticate": "Bearer"},
        )
