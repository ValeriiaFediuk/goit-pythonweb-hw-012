from typing import List

from sqlalchemy import select, or_, and_, func, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import timedelta

from src.database.models import Contact, User
from src.schemas.contacts import ContactBase, ContactResponse


class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(self, skip: int, limit: int, user: User) -> List[Contact]:
        """
        Fetches a list of contacts for a given user with pagination support.

        Args:
            skip (int): The number of records to skip (used for pagination).
            limit (int): The maximum number of records to return (used for pagination).
            user (User): The user whose contacts are to be fetched.

        Returns:
            List[Contact]: A list of contacts for the user.
        """
        stmt = select(Contact).filter_by(user=user).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        """
        Retrieves a contact by its ID for a specific user.

        Args:
            contact_id (int): The ID of the contact to retrieve.
            user (User): The user whose contact is to be fetched.

        Returns:
            Contact | None: The contact if found, or None if not found.
        """
        stmt = select(Contact).filter_by(user=user, id=contact_id)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactBase, user: User) -> Contact:
        """
        Creates a new contact for the specified user.

        Args:
            body (ContactBase): The contact data used to create the new contact.
            user (User): The user to associate the new contact with.

        Returns:
            Contact: The newly created contact.
        """
        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        """
        Deletes a contact by its ID for the specified user.

        Args:
            contact_id (int): The ID of the contact to delete.
            user (User): The user whose contact is to be deleted.

        Returns:
            Contact | None: The deleted contact if found, or None if not found.
        """
        contact = await self.get_contact_by_id(contact_id, user=user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactBase, user: User
    ) -> Contact | None:
        """
        Updates a contact by its ID for the specified user.

        Args:
            contact_id (int): The ID of the contact to update.
            body (ContactBase): The new contact data to update the contact with.
            user (User): The user whose contact is to be updated.

        Returns:
            Contact | None: The updated contact if found, or None if not found.
        """
        contact = await self.get_contact_by_id(contact_id, user=user)
        if contact:
            for key, value in body.dict(exclude_unset=True).items():
                setattr(contact, key, value)

            await self.db.commit()
            await self.db.refresh(contact)

        return contact

    async def search_contacts(
        self, search: str, skip: int, limit: int, user: User
    ) -> List[Contact]:
        """
        Searches for contacts that match the specified search string.

        Args:
            search (str): The search string used to find matching contacts.
            skip (int): The number of records to skip (used for pagination).
            limit (int): The maximum number of records to return (used for pagination).
            user (User): The user whose contacts are to be searched.

        Returns:
            List[Contact]: A list of contacts that match the search criteria.
        """
        stmt = (
            select(Contact)
            .filter(
                Contact.user == user,
                or_(
                    Contact.first_name.ilike(f"%{search}%"),
                    Contact.last_name.ilike(f"%{search}%"),
                    Contact.email.ilike(f"%{search}%"),
                    Contact.additional_data.ilike(f"%{search}%"),
                    Contact.phone_number.ilike(f"%{search}%"),
                )
            )
            .offset(skip)
            .limit(limit)
        )
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def upcoming_birthdays(self, days: int, user: User) -> List[Contact]:
        """
        Retrieves a list of contacts who have birthdays within the next specified number of days.

        Args:
            days (int): The number of days from today to check for upcoming birthdays.
            user (User): The user whose contacts are to be checked.

        Returns:
            List[Contact]: A list of contacts with upcoming birthdays.
        """
        today = func.current_date()
        future_date = today + timedelta(days=days)
        stmt = select(Contact).filter(
            Contact.user == user,
            or_(
                and_(
                    extract("month", Contact.birthday) == extract("month", today),
                    extract("day", Contact.birthday) >= extract("day", today),
                ),
                and_(
                    extract("month", Contact.birthday) == extract("month", future_date),
                    extract("day", Contact.birthday) <= extract("day", future_date),
                ),
            )
        )
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()