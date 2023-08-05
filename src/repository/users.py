from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status
from src.database.models import User
from src.schemas.user_schemas import UserModel, UserUpdate, UserBlackList


async def get_user_by_email(email: str, db: Session) -> User | None:
    """
The get_user_by_email function takes in an email and a database session, then returns the user with that email.

:param email: str: Pass in the email of the user we want to find
:param db: Session: Pass the database session into the function
:return: A user if the email is found in the database

    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
The create_user function creates a new user in the database.
    If there are no users with admin role, then the first created user will be an admin.
    Otherwise, all subsequent users will have 'user' role.

:param body: UserModel: Create a new user
:param db: Session: Access the database
:return: A user object

    """
    admin_exists = db.query(User).filter(User.role == 'admin').first()

    if admin_exists:
        new_user = User(**body.dict(), role='user')
    else:
        new_user = User(**body.dict(),  role='admin')

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
The update_token function updates the refresh token for a user.
    Args:
        user (User): The User object to update.
        token (str | None): The new refresh token to set for the user. If None, then no change is made to the current value of this field in the database.

:param user: User: Identify which user the token is being updated for
:param token: str | None: Pass in the token that is returned from the spotify api
:param db: Session: Access the database
:return: None

    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
The confirmed_email function takes in an email and a database session,
and sets the confirmed field of the user with that email to True.


:param email: str: Get the email of the user
:param db: Session: Pass the database session to the function
:return: None

    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def get_user_info(username: str, db: Session):
    """
The get_user_info function takes in a username and returns the user's information.
    Args:
        username (str): The name of the user to be retrieved from the database.

:param username: str: Pass the username of the user to be retrieved
:param db: Session: Pass in the database session to the function
:return: A user object

    """
    user = db.query(User).filter(User.username == username).first()
    return user


async def update_user_info(body: UserUpdate, username: str, db: Session):
    """
The update_user_info function updates a user's information in the database.

:param body: UserUpdate: Get the data from the request body
:param username: str: Get the user from the database
:param db: Session: Pass the database session to the function
:return: The user object

    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.username = body.username
    user.email = body.email
    db.commit()
    return user


async def block(email: str, body: UserBlackList, db: Session):
    """
The block function takes in an email and a body containing the banned status of the user.
It then finds that user by their email, sets their banned status to whatever is passed in,
and returns that user.

:param email: str: Get the user by email
:param body: UserBlackList: Get the banned status of a user
:param db: Session: Pass the database session to the function
:return: A user object

    """
    user = await get_user_by_email(email, db)
    if user:
        user.banned = body.banned
        db.commit()
    return user
