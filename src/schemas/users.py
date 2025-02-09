from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator
from src.database.models import UserRole

class User(BaseModel):
    """
    Schema representing a user in the system.

    This schema is used for defining user details, such as the username, email, avatar,
    confirmation status, and role. It is used in the response model to return user information.

    Attributes:
        id (int): The unique identifier of the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        avatar (str): The URL of the user's avatar image.
        confirmed (bool): The user's email confirmation status (default: False).
        role (UserRole): The user's role in the system (e.g., USER, ADMIN).
    """
    id: int
    username: str
    email: str
    avatar: str
    confirmed: bool = False
    role: UserRole

    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    """
    Schema for creating a new user account.

    This schema defines the fields required for registering a new user, including the
    username, email, password, and role.

    Attributes:
        username (str): The desired username of the user.
        email (str): The email address of the user.
        password (str): The password for the user's account.
        role (UserRole): The role of the user (e.g., USER or ADMIN).
    """
    username: str
    email: str
    password: str
    role: UserRole


class UserLogin(BaseModel):
    """
    Schema for user login.

    This schema is used for logging in a user with their email and password.

    Attributes:
        email (str): The email address of the user.
        password (str): The password for the user's account.
    """
    email: str
    password: str


class Token(BaseModel):
    """
    Schema for representing an authentication token.

    This schema is used for returning an access token and its type (usually "bearer")
    after a successful login or token refresh.

    Attributes:
        access_token (str): The authentication token for accessing protected resources.
        token_type (str): The type of the token, typically "bearer".
    """
    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    """
    Schema for requesting a password reset by email.

    This schema is used for sending a password reset request based on the user's email.

    Attributes:
        email (EmailStr): The email address of the user requesting a password reset.
    """
    email: EmailStr


class PasswordResetRequest(BaseModel):
    """
    Schema for initiating a password reset process.

    This schema is used for requesting a password reset by email.

    Attributes:
        email (EmailStr): The email address of the user requesting the password reset.
    """
    email: EmailStr
    

class PasswordResetConfirm(BaseModel):
    """
    Schema for confirming a password reset.

    This schema is used for confirming the password reset by providing the token and new password.

    Attributes:
        token (str): The password reset token sent to the user.
        new_password (str): The new password to be set for the user's account.
    """
    token: str
    new_password: str