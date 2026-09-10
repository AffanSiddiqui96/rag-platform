from pydantic import BaseModel, EmailStr

# Base properties shared across schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

# Schema for incoming request data (Creating a User)
class UserCreate(UserBase):
    password: str

# Schema for outgoing response data (Reading a User)
class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        # Crucial: Allows Pydantic to read SQLAlchemy ORM models natively
        from_attributes = True 

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"