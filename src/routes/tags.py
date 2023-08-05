from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User, Role
from src.schemas.tag_schemas import TagModel, TagResponse
from src.repository import tags as repository_tags
from src.conf.messages import AuthMessages

from src.services.auth import auth_service
from src.services.roles import RolesAccess

router = APIRouter(prefix='/tags', tags=["tags"])

access_get = RolesAccess([Role.admin, Role.moderator, Role.user])
access_create = RolesAccess([Role.admin, Role.moderator, Role.user])
access_update = RolesAccess([Role.admin, Role.moderator])
access_delete = RolesAccess([Role.admin, Role.moderator])


@router.get("/", response_model=List[TagResponse], dependencies=[Depends(access_get)])
async def read_tags(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _: User = Depends(auth_service.get_current_user)):
    """
The read_tags function returns a list of tags.

:param skip: int: Skip the first n tags, where n is the value of skip
:param limit: int: Determine the number of tags to return
:param db: Session: Pass the database session to the repository
:param _: User: Make sure that the user is authenticated before they can access this route
:return: A list of tag objects

    """
    tags = await repository_tags.get_tags(skip, limit, db)
    return tags


@router.get("/{tag_id}", response_model=TagResponse, dependencies=[Depends(access_get)])
async def read_tag(tag_id: int, db: Session = Depends(get_db), _: User = Depends(auth_service.get_current_user)):
    """
The read_tag function will return a single tag from the database.
    The function takes in an integer, which is the id of the tag to be returned.
    If no such tag exists, then a 404 error is raised.

:param tag_id: int: Specify the id of the tag to be deleted
:param db: Session: Access the database
:param _: User: Check if the user is logged in
:return: A tag object

    """
    tag = await repository_tags.get_tag(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag


@router.post("/", response_model=TagResponse, dependencies=[Depends(access_create)])
async def create_tag(body: TagModel, db: Session = Depends(get_db), _: User = Depends(auth_service.get_current_user)):
    """
The create_tag function creates a new tag in the database.
    It takes a TagModel object as input and returns the created tag.


:param body: TagModel: Get the body of the request and validate it
:param db: Session: Get the database session
:param _: User: Check if the user is authenticated
:return: A tagmodel object

    """
    check_tag = await repository_tags.get_tag_by_name(body.name.lower(), db)
    if check_tag:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Such tag already exist')
    tag = await repository_tags.create_tag(body, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=AuthMessages.verification_error)
    return tag


@router.put("/{tag_id}", response_model=TagResponse, dependencies=[Depends(access_update)])
async def update_tag(body: TagModel, tag_id: int, db: Session = Depends(get_db), _: User = Depends(auth_service.get_current_user)):
    """
The update_tag function updates a tag in the database.
    The function takes an id of the tag to update, and a body containing the new values for that tag.
    It returns an updated version of that same TagModel object.

:param body: TagModel: Get the data from the request body
:param tag_id: int: Get the tag id from the url
:param db: Session: Get the database session
:param _: User: Check if the user is logged in
:return: A tag object

    """
    tag = await repository_tags.update_tag(tag_id, body, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Tag not found or exists or you don't have enough rules to update")
    return tag


@router.delete("/{tag_id}", response_model=TagResponse, dependencies=[Depends(access_delete)])
async def remove_tag(tag_id: int, db: Session = Depends(get_db), _: User = Depends(auth_service.get_current_user)):
    """
The remove_tag function removes a tag from the database.
    It takes in an integer representing the id of the tag to be removed, and returns a dictionary containing information about that tag.


:param tag_id: int: Specify the id of the tag to be deleted
:param db: Session: Pass the database session to the function
:param _: User: Check if the user is authenticated
:return: A tag object

    """
    tag = await repository_tags.remove_tag(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Tag not found or you don't have enough rules to delete")
    return tag
