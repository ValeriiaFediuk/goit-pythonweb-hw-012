from typing import List

from sqlalchemy import select, or_, and_, func, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import timedelta

from src.database.models import Contact
from src.schemas.contacts import ContactBase, ContactResponse


class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(self, skip: int, limit: int) -> List[Contact]:
        stmt = select(Contact).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int) -> Contact | None:
        stmt = select(Contact).filter_by(id=contact_id)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactBase) -> Contact:
        contact = Contact(**body.model_dump(exclude_unset=True))
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def remove_contact(self, contact_id: int) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactBase
    ) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id)
        if contact:
            for key, value in body.dict(exclude_unset=True).items():
                setattr(contact, key, value)

            await self.db.commit()
            await self.db.refresh(contact)

        return contact

    async def search_contacts(
        self, search: str, skip: int, limit: int
    ) -> List[Contact]:
        stmt = (
            select(Contact)
            .filter(
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

    async def upcoming_birthdays(self, days: int = 7) -> List[Contact]:
        today = func.current_date()
        future_date = today + timedelta(days=days)
        stmt = select(Contact).filter(
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