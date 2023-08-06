import pytest
from sqlalchemy.orm import Session

from src.database.models import User
from src.repository.users import get_user_by_email, update_token, confirmed_email, get_user_info, update_user_info


@pytest.mark.asyncio
async def test_get_user_by_email(session: Session):
    """
The test_get_user_by_email function tests the get_user_by_email function in the users.py file.
It creates a user with an email address, adds it to the database, and then calls get_user_by_email
with that email address as an argument. It asserts that this call returns a User object with
the same email address.

:param session: Session: Pass in a sqlalchemy session object, which is used to query the database
:return: A user object
:doc-author: Trelent
    """
    email = "test@example.com"
    user = User(username="testuser", email=email, password="password")
    session.add(user)
    session.commit()

    result = await get_user_by_email(email, session)

    assert result is not None
    assert result.email == email


@pytest.mark.asyncio
async def test_update_token(session: Session):
    """
The test_update_token function tests the update_token function.
It creates a user, adds it to the database, and commits it.
Then it calls update_token with that user and a token string.
Finally, we refresh our session so that we can check if the token was updated.

:param session: Session: Pass in the database session to the function
:return: A coroutine, which is a special type of object that can be used with asyncio
:doc-author: Trelent
    """
    user = User(username="testuser", email="test@example.com", password="password")
    session.add(user)
    session.commit()
    token = "new_token"

    await update_token(user, token, session)

    session.refresh(user)
    assert user.refresh_token == token


@pytest.mark.asyncio
async def test_confirmed_email(session: Session):
    """
The test_confirmed_email function tests the confirmed_email function.
    It creates a user with an email address and confirms that the user's email is not confirmed.
    Then it calls the confirmed_email function to confirm that user's email address, and then checks again to make sure
    that their email has been successfully marked as &quot;confirmed&quot;.

:param session: Session: Pass in the database session
:return: A boolean value
:doc-author: Trelent
    """
    email = "test@example.com"
    user = User(username="testuser", email=email, password="password", confirmed=False)
    session.add(user)
    session.commit()

    await confirmed_email(email, session)

    confirmed_user = await get_user_by_email(email, session)
    assert confirmed_user.confirmed is True


@pytest.mark.asyncio
async def test_get_user_info(session: Session):
    """
The test_get_user_info function tests the get_user_info function.
It does this by creating a user in the database, then calling get_user_info with that username.
The test passes if the returned UserInfo object has all of its fields set to what we expect.

:param session: Session: Pass in a database session to the function
:return: A user object
:doc-author: Trelent
    """
    username = "testuser"
    user = User(username=username, email="test@example.com", password="password")
    session.add(user)
    session.commit()

    user_info = await get_user_info(username, session)

    assert user_info is not None
    assert user_info.username == username
    assert user_info.email == "test@example.com"


@pytest.mark.asyncio
async def test_update_user_info(session: Session):
    """
The test_update_user_info function tests the update_user_info function.
It does so by creating a user, updating that user's information, and then asserting that the updated information is correct.

:param session: Session: Pass the database session to the function
:return: None
:doc-author: Trelent
    """
    username = "testuser"
    user = User(username=username, email="test@example.com", password="password")
    session.add(user)
    session.commit()

    updated_username = "newuser"
    updated_email = "new@example.com"
    updated_body = User(username=updated_username, email=updated_email)

    # Дія
    updated_user = await update_user_info(updated_body, username, session)

    # Assert
    assert updated_user is not None
    assert updated_user.username == updated_username
    assert updated_user.email == updated_email
