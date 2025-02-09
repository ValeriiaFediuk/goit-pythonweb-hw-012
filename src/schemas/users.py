from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator
from src.database.models import UserRole

# Схема користувача
class User(BaseModel):
    id: int
    username: str
    email: str
    avatar: str
    confirmed: bool = False
    role: UserRole

    model_config = ConfigDict(from_attributes=True)

# Схема для запиту реєстрації
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: UserRole


class UserLogin(BaseModel):
    email: str
    password: str


# Схема для токену
class Token(BaseModel):
    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    email: EmailStr

class PasswordResetRequest(BaseModel):
    email: EmailStr
    
class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str