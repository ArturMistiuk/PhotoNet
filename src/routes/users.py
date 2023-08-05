from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from src.database.db import get_db
from src.database.models import User, Role
from src.repository.users import get_user_info, update_user_info, block
from src.schemas.user_schemas import UserResponse, UserUpdate, UserBlackList, UserBlacklistResponse
from src.services.auth import auth_service
from src.services.roles import RolesAccess

access_get = RolesAccess([Role.admin, Role.moderator, Role.user])
access_create = RolesAccess([Role.admin, Role.moderator, Role.user])
access_update = RolesAccess([Role.admin, Role.moderator, Role.user])
access_delete = RolesAccess([Role.admin])
access_block = RolesAccess([Role.admin])

router = APIRouter(prefix="/users", tags=["Users profile"])


@router.get("/me/", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
The read_users_me function returns the current user's information.

:param current_user: User: Get the current user from the auth_service
:return: The current user

"""
    return current_user


@router.get("/{username}/", response_model=UserResponse)
async def profile_info(username: str, db: Session = Depends(get_db)):
    """
The profile_info function returns the user's profile information.

:param username: str: Specify the username of the user whose profile is being requested
:param db: Session: Pass the database session to the function
:return: A user object

    """
    user_info = await get_user_info(username, db)
    if user_info is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_info


@router.put('/{username}', response_model=UserResponse, dependencies=[Depends(access_update)])
async def profile_update(username: str, body: UserUpdate, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
The profile_update function updates the user's profile information.
    The function takes in a username, body (which contains the updated info), db, and current_user.
    If the current_user is not an admin or does not match with the username provided, then they are forbidden from updating this profile.
    Otherwise, update_user_info is called to update their information.

:param username: str: Get the username of the user to be deleted
:param body: UserUpdate: Get the data from the user
:param db: Session: Access the database
:param current_user: User: Get the current user's information
:return: The updated user object

    """
    if current_user.username != username and current_user.role == 'user':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own profile")

    updated_user = await update_user_info(body, username, db)

    return updated_user


@router.patch("/{email}/blacklist", response_model=UserBlacklistResponse, dependencies=[Depends(access_block)])
async def block_user(email: str, body: UserBlackList, db: Session = Depends(get_db),
                        _: User = Depends(auth_service.get_current_user)):
    """
The block_user function is used to block a user from the system.
    The function takes in an email and a body of type UserBlackList, which contains the reason for blocking.
    It then calls the block function with these parameters, and returns either None or a blocked_user object.

:param email: str: Get the email of the user to be blocked
:param body: UserBlackList: Get the user_id and block_user_id from the request body
:param db: Session: Get the database session
:param _: User: Get the current user
:return: The blocked user object

    """
    blocked_user = await block(email, body, db)
    if blocked_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return blocked_user
