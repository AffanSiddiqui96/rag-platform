from pydantic import BaseModel, EmailStr, field_validator

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
    role: str

    class Config:
        # Crucial: Allows Pydantic to read SQLAlchemy ORM models natively
        from_attributes = True

    @field_validator("role", mode="before")
    @classmethod
    def extract_role_name(cls, value):
        # Accepts either the related Role ORM object or a plain string.
        return getattr(value, "role", value)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class DocumentUploadResponse(BaseModel):
    filename: str
    content_type: str
    size_bytes: int
    uploaded_by: str