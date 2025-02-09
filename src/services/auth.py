import json
from datetime import datetime, timedelta, UTC
from typing import Optional

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from src.database.db import get_db
from src.conf.config import settings
from src.services.users import UserService
from src.database.redis import redis_client
from src.schemas.users import User
from src.database.models import User, UserRole


class Hash:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        return self.pwd_context.hash(password)


oauth2_scheme = HTTPBearer()


# define a function to generate a new access token
async def create_access_token(data: dict, expires_delta: Optional[int] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)
    to_encode.update({"exp": expire})
    # print(to_encode)
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def create_reset_token(email: str) -> str:
    expire = datetime.now(UTC) + timedelta(seconds=app_config.RESET_TOKEN_EXPIRY)
    to_encode = {"sub": email, "exp": expire}
    return jwt.encode(
        to_encode, app_config.JWT_SECRET, algorithm=app_config.JWT_ALGORITHM
    )
def verify_reset_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            token, app_config.JWT_SECRET, algorithms=[app_config.JWT_ALGORITHM]
        )
        return payload["sub"]
    except JWTError:
        return None
    
async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT
        payload = jwt.decode(
            token.credentials, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        # print(payload)
        username = payload["sub"]
        if username is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception
    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    # Перевіряємо Redis
    cached_user = await redis_client.get(f"user:{username}")
    if cached_user:
        return json.loads(cached_user)
    # Якщо немає в Redis, звертаємось до БД
    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    # Кешуємо користувача в Redis
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }
    await redis_client.setex(f"user:{username}", 3600, json.dumps(user_data))

    return user


def create_email_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token

async def get_email_from_token(token: str):
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        email = payload["sub"]
        return email
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Невірний токен для перевірки електронної пошти",
        )
    
def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Недостатньо прав доступу")
    return current_user