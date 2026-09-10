from fastapi import FastAPI

from app.api.documents import router as documents_router
from app.api.hello import router as hello_router
from app.api.user import router as users_router
from app.exceptions import register_exception_handlers
from app.middleware.auth import AuthMiddleware


app = FastAPI(
    title="RAG Platform API",
    version="1.0.0",
)

# Security layer: blanket authentication for every route except the
# whitelisted public ones (see app/middleware/auth.py).
app.add_middleware(AuthMiddleware)

register_exception_handlers(app)

app.include_router(hello_router)
app.include_router(users_router)
app.include_router(documents_router)
