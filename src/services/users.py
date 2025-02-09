from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.repository.users import UserRepository
from src.schemas.users import UserCreate


class UserService:
    def __init__(self, db: AsyncSession):
        """
        Initializes the UserService with a database session.

        Args:
            db (AsyncSession): The database session to interact with the repository.
        """
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """
        Creates a new user and optionally fetches an avatar based on the user's email.
        
        Args:
            body (UserCreate): The user data for creation.
        
        Returns:
            User: The created user with the associated avatar URL.
        """
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int):
        """
        Fetch a user by their ID.
        
        Args:
            user_id (int): The ID of the user to retrieve.
        
        Returns:
            User | None: The user if found, or None if not found.
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        """
        Fetch a user by their username.
        
        Args:
            username (str): The username of the user to retrieve.
        
        Returns:
            User | None: The user if found, or None if not found.
        """
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        """
        Fetch a user by their email.
        
        Args:
            email (str): The email of the user to retrieve.
        
        Returns:
            User | None: The user if found, or None if not found.
        """
        return await self.repository.get_user_by_email(email)

    async def confirmed_email(self, email: str) -> None:
        """
        Marks the user's email as confirmed.
        
        Args:
            email (str): The email of the user to confirm.
        """
        return await self.repository.confirmed_email(email)

    async def update_avatar_url(self, email: str, url: str):
        """
        Updates the avatar URL for the user with the given email.
        
        Args:
            email (str): The email of the user whose avatar to update.
            url (str): The new avatar URL.
        
        Returns:
            User: The user with the updated avatar URL.
        """
        return await self.repository.update_avatar_url(email, url)
    
    async def update_password(self, email: str, new_password: str):
        """
        Updates the password for the user with the given email.
        
        Args:
            email (str): The email of the user whose password to update.
            new_password (str): The new password.
        """
        return await self.repository.update_password(email, new_password)