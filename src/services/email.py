from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import create_email_token, create_reset_token
from src.conf.config import settings

# Configure the mail server connection settings
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    Sends a confirmation email with a verification token to the user.

    Args:
        email (EmailStr): The recipient's email address.
        username (str): The username of the recipient.
        host (str): The host URL, usually for generating the full verification link.

    Returns:
        None: The function sends the email asynchronously.
    """
    try:
        # Generate email verification token
        token_verification = create_email_token({"sub": email})

        # Create the message schema
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        # Initialize FastMail and send the message
        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        print(f"Error sending email: {err}")


async def send_reset_email(email: str, username: str, host: str):
    """
    Sends a password reset email with a reset token to the user.

    Args:
        email (str): The recipient's email address.
        username (str): The username of the recipient.
        host (str): The host URL for generating the password reset link.

    Returns:
        None: The function sends the email asynchronously.
    """
    try:
        # Generate reset password token
        reset_token = create_reset_token(email)

        # Create the message schema for password reset email
        message = MessageSchema(
            subject="Password Reset Request",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": reset_token,
            },
            subtype=MessageType.html,
        )

        # Initialize FastMail and send the message
        fm = FastMail(conf)
        await fm.send_message(message, template_name="password_reset.html")
    except ConnectionErrors as err:
        print(f"Error sending password reset email: {err}")
