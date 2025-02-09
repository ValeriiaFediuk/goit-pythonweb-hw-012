from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.repository.contacts import ContactRepository
from src.schemas.contacts import ContactBase, ContactResponse


class ContactService:
    """
    Service class for handling contact-related operations. 
    This class interacts with the ContactRepository to perform CRUD operations on contacts.
    """
    def __init__(self, db: AsyncSession):
        """
        Initializes the ContactService with a given database session.

        Args:
            db (AsyncSession): The database session used for asynchronous operations.
        """
        self.contact_repository = ContactRepository(db)

    async def create_contact(self, body: ContactBase, user: User):
        """
        Creates a new contact for a specific user.

        Args:
            body (ContactBase): The contact data to be created.
            user (User): The user who is creating the contact.

        Returns:
            ContactResponse: The newly created contact data.
        """
        return await self.contact_repository.create_contact(body, user)

    async def get_contacts(self, skip: int, limit: int, user: User):
        """
        Retrieves a list of contacts for a specific user with pagination.

        Args:
            skip (int): The number of contacts to skip for pagination.
            limit (int): The maximum number of contacts to retrieve.
            user (User): The user whose contacts are being fetched.

        Returns:
            List[ContactResponse]: A list of contacts for the user.
        """
        return await self.contact_repository.get_contacts(skip, limit, user)

    async def get_contact(self, contact_id: int, user: User):
        """
        Retrieves a single contact by ID for a specific user.

        Args:
            contact_id (int): The ID of the contact to retrieve.
            user (User): The user whose contact is being fetched.

        Returns:
            ContactResponse: The contact data for the given ID.
        """
        return await self.contact_repository.get_contact_by_id(contact_id, user)

    async def update_contact(self, contact_id: int, body: ContactBase, user: User):
        """
        Updates an existing contact's details.

        Args:
            contact_id (int): The ID of the contact to update.
            body (ContactBase): The new contact data to update.
            user (User): The user updating the contact.

        Returns:
            ContactResponse: The updated contact data.
        """
        return await self.contact_repository.update_contact(contact_id, body, user)

    async def remove_contact(self, contact_id: int, user: User):
        """
        Removes a contact by ID for a specific user.

        Args:
            contact_id (int): The ID of the contact to remove.
            user (User): The user deleting the contact.

        Returns:
            None: This method does not return any value.
        """
        return await self.contact_repository.remove_contact(contact_id, user)

    async def search_contacts(self, search: str, skip: int, limit: int, user: User):
        """
        Searches for contacts by a given search query, with pagination.

        Args:
            search (str): The search query to find matching contacts.
            skip (int): The number of contacts to skip for pagination.
            limit (int): The maximum number of contacts to retrieve.
            user (User): The user whose contacts are being searched.

        Returns:
            List[ContactResponse]: A list of contacts matching the search query.
        """
        return await self.contact_repository.search_contacts(search, skip, limit, user)

    async def upcoming_birthdays(self, days: int, user: User):
        """
        Retrieves a list of contacts with upcoming birthdays within the specified number of days.

        Args:
            days (int): The number of days within which to check for upcoming birthdays.
            user (User): The user whose contacts' birthdays are being checked.

        Returns:
            List[ContactResponse]: A list of contacts with upcoming birthdays.
        """
        return await self.contact_repository.upcoming_birthdays(days, user)