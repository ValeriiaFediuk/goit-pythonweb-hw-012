from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas.contacts import ContactBase, ContactResponse, ContactBirthdayRequest
from src.services.contacts import ContactService
from src.services.auth import get_current_user
from src.database.models import User
from src.conf import messages

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse], status_code=status.HTTP_200_OK)
async def read_contacts(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    """
    Retrieve a list of contacts for the current user, with optional pagination.

    Args:
        skip (int): The number of records to skip for pagination (default is 0).
        limit (int): The maximum number of records to return (default is 100).
        db (AsyncSession): The database session dependency.
        user (User): The current user (retrieved from OAuth2 token).

    Returns:
        List[ContactResponse]: A list of contacts belonging to the current user.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(skip, limit, user)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(contact_id: int, 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)):
    """
    Retrieve a specific contact by ID for the current user.

    Args:
        contact_id (int): The ID of the contact to retrieve.
        db (AsyncSession): The database session dependency.
        user (User): The current user (retrieved from OAuth2 token).

    Returns:
        ContactResponse: The contact information.

    Raises:
        HTTPException: If the contact is not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND
        )
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactBase, 
    db: AsyncSession = Depends(get_db), 
    user: User = Depends(get_current_user)):
    """
    Create a new contact for the current user.

    Args:
        body (ContactBase): The contact data to create.
        db (AsyncSession): The database session dependency.
        user (User): The current user (retrieved from OAuth2 token).

    Returns:
        ContactResponse: The created contact.
    """
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, user)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactBase, contact_id: int, 
    db: AsyncSession = Depends(get_db), 
    user: User = Depends(get_current_user)
): 
    """
    Update an existing contact for the current user.

    Args:
        body (ContactBase): The updated contact data.
        contact_id (int): The ID of the contact to update.
        db (AsyncSession): The database session dependency.
        user (User): The current user (retrieved from OAuth2 token).

    Returns:
        ContactResponse: The updated contact information.

    Raises:
        HTTPException: If the contact is not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND
        )
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_contact(contact_id: int, db: AsyncSession = Depends(get_db), 
    user: User = Depends(get_current_user)):
    """
    Delete a contact by ID for the current user.

    Args:
        contact_id (int): The ID of the contact to delete.
        db (AsyncSession): The database session dependency.
        user (User): The current user (retrieved from OAuth2 token).

    Raises:
        HTTPException: If the contact is not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.remove_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND
        )
    return


@router.get("/search/", response_model=List[ContactResponse])
async def search_contacts(
    text: str, skip: int = 0, limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Search for contacts based on a search text for the current user.

    Args:
        text (str): The search query.
        skip (int): The number of records to skip for pagination (default is 0).
        limit (int): The maximum number of records to return (default is 100).
        db (AsyncSession): The database session dependency.
        user (User): The current user (retrieved from OAuth2 token).

    Returns:
        List[ContactResponse]: A list of contacts matching the search query.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.search_contacts(text, skip, limit)
    return contacts


@router.post("/upcoming-birthdays", response_model=List[ContactResponse])
async def upcoming_birthdays(
    body: ContactBirthdayRequest, 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Retrieve a list of contacts who have upcoming birthdays based on the given number of days.

    Args:
        body (ContactBirthdayRequest): The number of days to look ahead for upcoming birthdays.
        db (AsyncSession): The database session dependency.
        user (User): The current user (retrieved from OAuth2 token).

    Returns:
        List[ContactResponse]: A list of contacts with upcoming birthdays.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.upcoming_birthdays(body.days)
    return contacts