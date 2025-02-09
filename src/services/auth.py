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
    """
    Class for hashing and verifying passwords using the bcrypt hashing algorithm.

    This class provides methods to verify a plain password against a hashed password
    and to hash a plain password.

    Methods:
        verify_password(plain_password: str, hashed_password: str) -> bool:
            Verifies if the plain password matches the hashed password.
        
        get_password_hash(password: str) -> str:
            Returns a hashed version of the given password.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        """
        Verifies if the plain password matches the hashed password.
        
        Args:
            plain_password (str): The plain text password.
            hashed_password (str): The hashed version of the password.
        
        Returns:
            bool: True if the passwords match, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Hashes the given password using bcrypt.
        
        Args:
            password (str): The plain password to be hashed.
        
        Returns:
            str: The hashed password.
        """
        return self.pwd_context.hash(password)


oauth2_scheme = HTTPBearer()


async def create_access_token(data: dict, expires_delta: Optional[int] = None):
    """
    Generates a new access token.

    This function creates a JWT token that contains the user data and expires after a set period.

    Args:
        data (dict): The data to be encoded into the token.
        expires_delta (Optional[int]): The expiration time in seconds. If not provided, the default expiration time is used.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def create_reset_token(email: str) -> str:
    """
    Creates a reset token for password recovery.

    Args:
        email (str): The user's email address to be encoded in the reset token.

    Returns:
        str: The encoded JWT reset token.
    """
    expire = datetime.now(UTC) + timedelta(seconds=app_config.RESET_TOKEN_EXPIRY)
    to_encode = {"sub": email, "exp": expire}
    return jwt.encode(
        to_encode, app_config.JWT_SECRET, algorithm=app_config.JWT_ALGORITHM
    )
def verify_reset_token(token: str) -> str | None:
    """
    Verifies a password reset token and retrieves the associated email.

    Args:
        token (str): The password reset token to verify.

    Returns:
        str | None: The email encoded in the token if the token is valid, None otherwise.
    """
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
    """
    Retrieves the currently authenticated user from the token.

    This function decodes the provided JWT token, validates it, and fetches the user 
    associated with the username from the database. The user is also cached in Redis.

    Args:
        token (HTTPAuthorizationCredentials): The JWT token for the user.
        db (Session): The database session.

    Returns:
        User: The authenticated user object.

    Raises:
        HTTPException: If the credentials are invalid or the user is not found.
    """
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
    """
    Creates a JWT token for email verification.

    Args:
        data (dict): The data to be encoded in the email verification token.

    Returns:
        str: The encoded JWT email verification token.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token

async def get_email_from_token(token: str):
    """
    Extracts the email from the email verification token.

    Args:
        token (str): The email verification token to decode.

    Returns:
        str: The email extracted from the token.

    Raises:
        HTTPException: If the token is invalid.
    """
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
    """
    Retrieves the currently authenticated admin user.

    This function ensures that the authenticated user has the 'ADMIN' role.

    Args:
        current_user (User): The current authenticated user.

    Returns:
        User: The authenticated admin user.

    Raises:
        HTTPException: If the user does not have admin rights.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Недостатньо прав доступу")
    return current_user