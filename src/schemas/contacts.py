from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator

from src.conf import messages

class ContactBase(BaseModel):
    """
    Base schema for creating and updating contact information.

    This schema is used for defining the core contact fields such as first name,
    last name, email, phone number, birthday, and additional data. It includes 
    validators for birthday and phone number.

    Attributes:
        first_name (str): The first name of the contact.
        last_name (str): The last name of the contact.
        email (EmailStr): The email address of the contact.
        phone_number (str): The phone number of the contact.
        birthday (date): The birthdate of the contact.
        additional_data (Optional[str]): Any additional information about the contact.
    """
    first_name: str = Field(max_length=50, min_length=2)
    last_name: str = Field(max_length=50, min_length=2)
    email: EmailStr
    phone_number: str = Field(max_length=20, min_length=6)
    birthday: date
    additional_data: Optional[str] = Field(max_length=150)

    @field_validator("birthday")
    def validate_birthday(cls, v):
        """
        Validator for the 'birthday' field to ensure it is not in the future.

        Args:
            v (date): The birthdate to validate.

        Raises:
            ValueError: If the birthday is in the future.
        
        Returns:
            date: The validated birthday.
        """
        if v > date.today():
            raise ValueError(messages.INVALID_BIRTHDAY)
        return v

    @field_validator("phone_number")
    def validate_phone_number(cls, v):
        """
        Validator for the 'phone_number' field to ensure it contains only digits.

        Args:
            v (str): The phone number to validate.

        Raises:
            ValueError: If the phone number contains non-digit characters.
        
        Returns:
            str: The validated phone number.
        """
        if not v.isdigit():
            raise ValueError(messages.INVALID_PHONE_NUMBER)
        return v


class ContactResponse(ContactBase):
    """
    Response schema for returning contact information, including timestamps.

    This schema extends `ContactBase` and includes additional fields for the 
    contact's creation and update timestamps.

    Attributes:
        id (int): The unique identifier of the contact.
        created_at (Optional[datetime]): The timestamp when the contact was created.
        updated_at (Optional[datetime]): The timestamp when the contact was last updated.
    """
    id: int
    created_at: datetime | None
    updated_at: Optional[datetime] | None

    model_config = ConfigDict(from_attributes=True)


class ContactBirthdayRequest(BaseModel):
    """
    Schema for requesting contacts with upcoming birthdays.

    This schema defines the number of days in advance to check for birthdays.

    Attributes:
        days (int): The number of days to check for upcoming birthdays (0 to 366).
    """
    days: int = Field(ge=0, le=366)