from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["Nguyễn Văn A"])
    email: EmailStr = Field(..., examples=["nguyenvana@example.com"])
    phone: Optional[str] = Field(None, max_length=20, examples=["0901234567"])
    role: Optional[str] = Field("user", examples=["user", "admin"])
    is_active: Optional[bool] = True


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str]
    role: str
    is_active: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}
