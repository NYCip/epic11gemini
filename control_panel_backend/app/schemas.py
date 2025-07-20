from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from .models import UserRole

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = UserRole.VIEWER

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

class SystemStatus(BaseModel):
    status: str
    services: dict
    uptime: float
    version: str = "v11.0.0"

class AuditLogEntry(BaseModel):
    action: str
    resource: Optional[str] = None
    details: Optional[dict] = None

class SystemOverrideRequest(BaseModel):
    action: str = Field(..., pattern="^(HALT|RESUME|EMERGENCY)$")
    reason: str
    confirmation_code: Optional[str] = None  # For extra security
