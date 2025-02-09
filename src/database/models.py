from datetime import datetime, date
from enum import Enum

from sqlalchemy import Column, Integer, String, Boolean, func, Table, Enum as SqlEnum
from sqlalchemy.orm import relationship, mapped_column, Mapped, DeclarativeBase
from sqlalchemy.sql.schema import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.sql.sqltypes import DateTime, Date


class UserRole(str, Enum):
    """
    Enum representing the roles a user can have.

    Attributes:
        USER (str): Regular user role.
        ADMIN (str): Administrator role with higher privileges.
    """
    USER = "USER"
    ADMIN = "ADMIN"

class Base(DeclarativeBase):
    """
    Base class for all models in the application.

    Contains common fields like `created_at` and `updated_at` to track the
    creation and modification timestamps of records.

    Attributes:
        created_at (datetime): Timestamp when the record is created.
        updated_at (datetime): Timestamp when the record is last updated.
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

class Contact(Base):
    """
    Represents a contact in the application.

    The `Contact` model stores personal information about a user and is associated
    with the `User` model through the `user_id` field. It also includes fields for
    storing contact details, such as the name, email, phone number, and birthday.

    Attributes:
        id (int): Primary key for the contact.
        first_name (str): The contact's first name.
        last_name (str): The contact's last name.
        email (str): The contact's email address.
        phone_number (str): The contact's phone number.
        birthday (date): The contact's birthday.
        additional_data (str): Optional field for any additional contact details.
        user_id (int): Foreign key referring to the associated user.
        user (User): Relationship to the `User` model, where this contact belongs to a specific user.
    """
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    birthday: Mapped[date] = mapped_column(Date, nullable=False)
    additional_data: Mapped[str] = mapped_column(String(150), nullable=True)
    user_id = Column(
        "user_id", ForeignKey("users.id", ondelete="CASCADE"), default=None
    )
    user = relationship("User", backref="contacts")


class User(Base):
    """
    Represents a user in the application.

    The `User` model stores information about the application's users, including their
    login credentials, avatar, role, and confirmation status.

    Attributes:
        id (int): Primary key for the user.
        username (str): The user's username (unique).
        email (str): The user's email address (unique).
        hashed_password (str): The hashed password of the user.
        created_at (datetime): Timestamp when the user was created.
        avatar (str): URL or path to the user's avatar image.
        confirmed (bool): Indicates if the user's email has been confirmed.
        role (UserRole): The user's role (either 'USER' or 'ADMIN').
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    role = Column(SqlEnum(UserRole), default=UserRole.USER, nullable=False)