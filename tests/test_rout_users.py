from unittest.mock import MagicMock, patch

import pytest

from src.database.models import User
from src.services.auth import auth_service


@pytest.fixture()
def token(client, user, session, monkeypatch):
    """
The token function is used to create a token for the user.
    It takes in the client, user, session and monkeypatch as arguments.
    The mock_send_email function is created using MagicMock() from unittest.mock library and
    it replaces the send_email function with mock_send_email function which does nothing but return None when called.
     This helps us avoid sending emails during testing since we are not concerned about that functionality here.

:param client: Make requests to the api
:param user: Create a new user
:param session: Create a new session for the test
:param monkeypatch: Mock the send_email function
:return: The access token
:doc-author: Trelent
"""
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    client.post("/api/auth/signup", json=user)
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    data = response.json()
    return data["access_token"]


def test_read_users_me_authenticated(client, token):
    """
The test_read_users_me_authenticated function tests that a user can read their own information.
It does this by first mocking the redis cache to return None, which will cause the auth_service to make a call
to the database for user data. It then makes an authenticated request with a valid token and checks that it returns
a 200 status code and contains all of the expected fields.

:param client: Make requests to the api
:param token: Pass the token to the test function
:return: A 200 status code and the user's username, email address, and password
:doc-author: Trelent
"""
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("api/users/me/", headers=headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert "username" in data
        assert "email" in data
        assert "password" not in data


def test_profile_info(client, token):
    """
The test_profile_info function tests the /api/users/&lt;username&gt; endpoint.
It does so by mocking out the auth_service's r object, which is a redis connection.
The mock returns None when it gets called with &quot;get&quot; and any arguments,
which simulates a user not being in the cache (i.e., they are not logged in).
Then we make an HTTP GET request to /api/users/deadpool/, passing our token as an Authorization header.

:param client: Make requests to the api
:param token: Test the authorization of the user
:return: The username and the status code
:doc-author: Trelent
"""
    with patch.object(auth_service, 'r') as r_mock:
            r_mock.get.return_value = None
            username = "deadpool"
            response = client.get(f"/api/users/{username}/",
                                  headers={"Authorization": f"Bearer {token}"})
            assert response.status_code == 200, response.text
            data = response.json()
            assert "username" in data
            assert data["username"] == username


def test_profile_info_user_not_found(client, token):
    """
The test_profile_info_user_not_found function tests the profile_info endpoint when a user is not found.
    It does this by mocking the redis get method to return None, which will cause an exception to be raised in
    auth_service.get_user(). This exception will then be caught and handled by our error handler, which returns a 404 status code.

:param client: Make requests to the api
:param token: Authenticate the user
:return: A 404 status code and a detail message
:doc-author: Trelent
"""
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        username = "not_deadpool"
        response = client.get(f"/api/users/{username}/",
                              headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "User not found"
