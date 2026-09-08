from fastapi import FastAPI
import logging

app = FastAPI()
logger = logging.getLogger(__name__)


@app.get("/")
async def read_root():
    logger.info("Root endpoint accessed")
    return {"Hello": "World"}


@app.get("/health")
async def read_health():
    logger.info("Health check endpoint accessed")
    return {"message": "App is running fine!"}

