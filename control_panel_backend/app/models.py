from sqlalchemy import Column, String, Boolean, DateTime, Enum, JSON, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.sql import func
import uuid
import enum
from .database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"

class Users(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(Enum(UserRole), nullable=False, default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))
    
class AuditLog(Base):
    __tablename__ = "audit_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String(255), nullable=False)
    resource = Column(String(255))
    details = Column(JSON)
    ip_address = Column(INET)
    user_agent = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
class SystemOverride(Base):
    __tablename__ = "system_override"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status = Column(String(50), nullable=False)  # HALT, RESUME, EMERGENCY
    initiated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    reason = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
