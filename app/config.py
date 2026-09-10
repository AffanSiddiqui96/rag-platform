import os

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, PostgresDsn

load_dotenv()

class Settings(BaseModel):
    ENV: str
    APP_NAME: str
    DATABASE_URL: PostgresDsn
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


settings = Settings(
        ENV=os.getenv("ENV"),
        APP_NAME=os.getenv("APP_NAME"),
        DATABASE_URL=os.getenv("DATABASE_URL"),
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY"),
        JWT_ALGORITHM=os.getenv("JWT_ALGORITHM", "HS256"),
        ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
    )

