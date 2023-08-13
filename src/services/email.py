from pathlib import Path

import logging
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from src.conf.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME="PhotoNet",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str):
    """
The send_email function sends an email to the user with a link to confirm their email address.
    The function takes in three parameters:
        -email: EmailStr, the user's email address.
        -username: str, the username of the user who is registering for an account.  This will be used in a greeting message within the body of the email sent to them.
        -host: str, this is where we are hosting our application (i.e., localhost).  This will be used as part of a URL that users can click on within their emails.

:param email: EmailStr: Specify the email address of the recipient
:param username: str: Pass the username of the user to be registered
:param host: str: Pass the hostname of the server to the email template
:return: A coroutine object

    """
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        logging.error(err)
