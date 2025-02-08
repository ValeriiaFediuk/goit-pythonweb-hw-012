from datetime import date, timedelta
from pprint import pprint
from unittest.mock import AsyncMock, MagicMock

import pytest
from conftest import test_user
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.repository.contacts import ContactRepository
from src.schemas.contacts import ContactBase
from tests.conftest import TestingSessionLocal

test_contacts = [
    {
        "first_name": "FName-1",
        "last_name": "LNAme-1",
        "email": "user-1@mail.com",
        "phone_number": "1111111111",
        "birthday": str(date(2010, 1, 10)),
        "additional_data": "text-1",
    },
    {
        "first_name": "FName-2",
        "last_name": "LNAme-2",
        "email": "user-2@mail.com",
        "phone_number": "1111111111",
        "birthday": str(date(2010, 12, 10)),
        "additional_data": "text-2",
    },
]


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def contact_repository(mock_session):
    return ContactRepository(mock_session)


@pytest.fixture
def user():
    return User(id=1, username=test_user["username"], email=test_user["email"])


@pytest.mark.asyncio
async def test_get_contacts(contact_repository, mock_session, user):
    # Setup mock
    mock_result = MagicMock()

    contacts_to_get = [
        Contact(
            id=i + 1,
            first_name=contact["first_name"],
            last_name=contact["last_name"],
            email=contact["email"],
            phone_number=contact["phone_number"],
            birthday=contact["birthday"],
            additional_data=contact["additional_data"],
            user=user,
        )
        for i, contact in enumerate(test_contacts[:2])
    ]

    mock_result.scalars.return_value.all.return_value = contacts_to_get
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    contacts = await contact_repository.get_contacts(skip=0, limit=10, user=user)
    # pprint([contact.__dict__ for contact in contacts])

    # Assertions
    assert len(contacts) == 2
    assert contacts[0].first_name == test_contacts[0]["first_name"]
    assert contacts[0].last_name == test_contacts[0]["last_name"]
    assert contacts[0].email == test_contacts[0]["email"]
    assert contacts[0].phone_number == test_contacts[0]["phone_number"]
    assert contacts[0].birthday == test_contacts[0]["birthday"]
    assert contacts[0].additional_data == test_contacts[0]["additional_data"]
    assert contacts == contacts_to_get


@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repository, mock_session, user):
    # Setup mock
    mock_result = MagicMock()
    contacts_to_get = [
        Contact(
            id=i + 1,
            first_name=contact["first_name"],
            last_name=contact["last_name"],
            email=contact["email"],
            phone_number=contact["phone_number"],
            birthday=contact["birthday"],
            additional_data=contact["additional_data"],
            user=user,
        )
        for i, contact in enumerate(test_contacts[:2])
    ]
    mock_result.scalar_one_or_none.return_value = contacts_to_get[0]
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    contact = await contact_repository.get_contact_by_id(contact_id=1, user=user)
    # pprint(contact.__dict__)

    # Assertions
    assert contact is not None
    assert contact.id == 1
    assert contact.first_name == test_contacts[0]["first_name"]


@pytest.mark.asyncio
async def test_create_contact_existing_user(contact_repository, mock_session, user):
    # Arrange
    body = ContactBase(
        first_name=test_contacts[0]["first_name"],
        last_name=test_contacts[0]["last_name"],
        email=test_contacts[0]["email"],
        phone_number=test_contacts[0]["phone_number"],
        birthday=test_contacts[0]["birthday"],
        additional_data=test_contacts[0]["additional_data"],
    )

    # Act
    contact = await contact_repository.create_contact(body, user)

    # Assert
    assert contact.user == user
    mock_session.add.assert_called_once_with(contact)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(contact)


@pytest.mark.asyncio
async def test_update_contact(contact_repository, mock_session, user):
    # Setup
    contact_old = Contact(
        id=1,
        first_name=test_contacts[0]["first_name"],
        last_name=test_contacts[0]["last_name"],
        email=test_contacts[0]["email"],
        phone_number=test_contacts[0]["phone_number"],
        birthday=test_contacts[0]["birthday"],
        additional_data=test_contacts[0]["additional_data"],
    )
    contact_new = ContactBase(
        first_name="updated first name",
        last_name="updated last name",
        email="updated@email.com",
        phone_number="1234567890",
        birthday=str(date(2020, 1, 1)),
        additional_data="updated additional data",
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = contact_old
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.update_contact(
        contact_id=1, body=contact_new, user=user
    )
    # pprint(result.__dict__)

    # Assertions
    assert result is not None
    assert result.first_name == contact_new.first_name
    assert result.last_name == contact_new.last_name
    assert result.email == contact_new.email
    assert result.phone_number == contact_new.phone_number
    assert result.birthday == contact_new.birthday
    assert result.additional_data == contact_new.additional_data
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(contact_old)


@pytest.mark.asyncio
async def test_remove_contact(contact_repository, mock_session, user):
    # Setup
    existing_contact = Contact(
        id=1,
        first_name=test_contacts[0]["first_name"],
        last_name=test_contacts[0]["last_name"],
        email=test_contacts[0]["email"],
        phone_number=test_contacts[0]["phone_number"],
        birthday=test_contacts[0]["birthday"],
        additional_data=test_contacts[0]["additional_data"],
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.remove_contact(contact_id=1, user=user)
    # pprint(result.__dict__)

    # Assertions
    assert result is not None
    assert result.first_name == existing_contact.first_name
    assert result.last_name == existing_contact.last_name
    assert result.email == existing_contact.email
    assert result.phone_number == existing_contact.phone_number
    assert result.birthday == existing_contact.birthday
    assert result.additional_data == existing_contact.additional_data
    mock_session.delete.assert_awaited_once_with(existing_contact)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_search_contacts_valid_query(
    contact_repository, mock_session, user, client
):
    user = User(id=0)
    contacts_to_db = [
        Contact(
            id=i + 1,
            first_name=contact["first_name"],
            last_name=contact["last_name"],
            email=contact["email"],
            phone_number=contact["phone_number"],
            birthday=date.fromisoformat(contact["birthday"]),
            additional_data=contact["additional_data"],
            user=user,
        )
        for i, contact in enumerate(test_contacts[:2])
    ]
    contact_to_search = contacts_to_db[0]

    async with TestingSessionLocal() as session:
        session.add_all(contacts_to_db)
        await session.commit()

        # Use the session in the repository
        contact_repository.db = session

        search_query = contact_to_search.first_name
        # search_query = "not-found-text"
        contacts = await contact_repository.search_contacts(
            search=search_query, skip=0, limit=100, user=user
        )
        # pprint([contact.__dict__ for contact in contacts])

    assert len(contacts) >= 1
    assert contact_to_search.id in [contact.id for contact in contacts]