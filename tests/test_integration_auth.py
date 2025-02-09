import pytest

from pprint import pprint
from unittest.mock import Mock

from fastapi import status
from sqlalchemy import select

from src.conf import messages
from src.database.models import User
from tests.conftest import TestingSessionLocal

user_data = {
    "username": "agent007",
    "email": "agent007@gmail.com",
    "password": "12345678",
    "role": "USER",
}

def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "hashed_password" not in data
    assert "avatar" in data

@pytest.mark.asyncio
async def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == messages.API_ERROR_USER_ALREADY_EXIST

def test_not_confirmed_login(client):
    response = client.post(
        "api/auth/login",
        json={
            "email": user_data.get("email"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.API_ERROR_USER_NOT_AUTHORIZED


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post(
        "api/auth/login",
        json={
            "email": user_data.get("email"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer", f'token_type should be {data["token_type"]}'


def test_wrong_password_login(client):
    response = client.post(
        "api/auth/login",
        json={"email": user_data.get("email"), "password": "wrong-password"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text
    data = response.json()
    assert data["detail"] == messages.API_ERROR_WRONG_PASSWORD

def test_wrong_username_login(client):
    response = client.post(
        "api/auth/login",
        json={"email": "wrong@email", "password": user_data.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.API_ERROR_WRONG_PASSWORD

def test_validation_error_login(client):
    response = client.post(
        "api/auth/login", json={"password": user_data.get("password")}
    )
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data

def test_request_email(client):
    response = client.post(
        "api/auth/request_email",
        json={"email": user_data.get("email")},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    # print(data)
    assert data["message"] == messages.API_EMAIL_CONFIRMED