from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
import os
import secrets
from .database import get_db
from . import models, schemas

# Security configurations
SECRET_KEY = os.getenv("JWT_SECRET", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/control/auth/token")

class AuthService:
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def get_current_user(
        self,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
    ) -> models.Users:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            role: str = payload.get("role")
            if email is None:
                raise credentials_exception
            token_data = schemas.TokenData(email=email, role=role)
        except JWTError:
            raise credentials_exception
        
        user = db.query(models.Users).filter(models.Users.email == token_data.email).first()
        if user is None:
            raise credentials_exception
        return user
    
    def get_current_active_user(
        self,
        current_user: models.Users = Depends(get_current_user)
    ) -> models.Users:
        if not current_user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user
    
    def require_role(self, allowed_roles: List[models.UserRole]):
        def role_checker(current_user: models.Users = Depends(self.get_current_active_user)):
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=403,
                    detail=f"Insufficient permissions. Required roles: {allowed_roles}"
                )
            return current_user
        return role_checker

# Global auth service instance
auth_service = AuthService()
