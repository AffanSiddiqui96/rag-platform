
import logging
from fastapi import APIRouter
from ..config import settings


router = APIRouter(
    prefix="/hello",
    tags=["health"],
)

logger = logging.getLogger(__name__)

@router.get("/")
async def read_root():
    logger.info("Root endpoint accessed")
    print(f"{settings.APP_NAME} started!")
    return {"Hello": "World"}


@router.get("/health")
async def read_health():
    logger.info("Health check endpoint accessed")
    print(f"We are in {settings.ENV} environment")
    return {"message": "App is running fine!"}

