import logging

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .config import settings
from utilities.auth import create_access_token
from utilities.hash_password import hash_password, verify_password
from utilities.model import UserModel
from utilities.schema import UserCreate, UserResponse, LoginRequest, LoginResponse



app = FastAPI()
logger = logging.getLogger(__name__)


engine = create_engine(str(settings.DATABASE_URL))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def read_root():
    logger.info("Root endpoint accessed")
    print(f"{settings.APP_NAME} started!")
    return {"Hello": "World"}


@app.get("/health")
async def read_health():
    logger.info("Health check endpoint accessed")
    print(f"We are in {settings.ENV} environment")
    return {"message": "App is running fine!"}


@app.post("/signup", response_model=UserResponse)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    # 1. Pydantic validates 'user_in' automatically
    db_user = UserModel(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
    )
    # 2. Save to database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # 3. Returns db_user, formatted automatically via UserResponse schema
    return db_user


@app.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == data.email).first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(str(user.id))

    return LoginResponse(access_token=access_token)