from typing import List

from fastapi import APIRouter, Depends, Path, HTTPException, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User, Role, Image
from src.schemas.comment_schemas import CommentResponse, CommentModel, CommentDeleteResponse
from src.repository import comments as repository_comments
from src.services.auth import auth_service
from src.services.roles import RolesAccess

router = APIRouter(prefix='/comments', tags=['comments'])

access_get = RolesAccess([Role.admin, Role.moderator, Role.user])
access_create = RolesAccess([Role.admin, Role.moderator, Role.user])
access_update = RolesAccess([Role.admin, Role.moderator, Role.user])
access_delete = RolesAccess([Role.admin, Role.moderator])


@router.get('/', response_model=List[CommentResponse],
            dependencies=[Depends(access_get)])
async def get_comments(db: Session = Depends(get_db), _: User = Depends(auth_service.get_current_user)):
    """
The get_comments function returns a list of comments.
    ---
    get:
      summary: Get all comments.
      description: Returns a list of all the comments in the database.  The user must be logged in to access this endpoint.  If not, an error will be returned instead of the comment data.

:param db: Session: Pass the database session to the function
:param _: User: Ensure that the user is logged in
:return: A list of comments

    """
    comments = await repository_comments.get_comments(db)
    return comments


@router.get('/{comment_id}', response_model=CommentResponse, dependencies=[Depends(access_get)])
async def get_comment_by_id(comment_id: int = Path(ge=1), db: Session = Depends(get_db),
                            _: User = Depends(auth_service.get_current_user)):
    """
The get_comment_by_id function returns a comment by its id.
    The function takes in the following parameters:
        - comment_id (int): The id of the comment to be returned.
        - db (Session): A database session object used for querying and updating data in the database.

:param comment_id: int: Get the comment id from the path,
:param db: Session: Get the database session
:param _: User: Ensure that the user is authenticated
:return: The comment with the given id

    """
    comment = await repository_comments.get_comment_by_id(comment_id, db)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such comment")
    return comment


@router.post('/', response_model=CommentResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(access_create)])
async def create_comment(body: CommentModel, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
The create_comment function creates a new comment in the database.
    It takes in a CommentModel object, which is validated by pydantic.
    The function then checks if the image_id exists in the database, and if not raises an error.
    If it does exist, it sets user_id to be equal to current_user's id (the logged-in user), and calls create_comment from repository/comments.py.

:param body: CommentModel: Validate the request body
:param db: Session: Get the database session
:param current_user: User: Get the current user's id
:return: A comment object

    """
    try:
        image = db.query(Image).filter_by(id=body.image_id).first()
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such image")
    body.user_id = current_user.id
    comment = await repository_comments.create_comment(body, db)
    return comment


@router.put('/{comment_id}', response_model=CommentResponse, dependencies=[Depends(access_update)])
async def update_comment(body: CommentModel, comment_id: int = Path(ge=1), db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
The update_comment function updates a comment in the database.
    The function takes an id of the comment to update, and a CommentModel object containing new data for that comment.
    If no such comment exists, it returns 404 Not Found error.


:param body: CommentModel: Get the body of the request
:param comment_id: int: Get the comment id from the url
:param db: Session: Access the database
:param current_user: User: Get the current user from the database
:return: A commentmodel object

    """
    if current_user.id != body.user_id and current_user.role == 'user':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't change not your comment")
    comment = await repository_comments.update_comment(body, comment_id, db)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such comment")
    return comment


@router.delete('/{comment_id}', response_model=CommentDeleteResponse, dependencies=[Depends(access_delete)])
async def remove_comment(comment_id: int = Path(ge=1), db: Session = Depends(get_db),
                         _: User = Depends(auth_service.get_current_user)):
    """
The remove_comment function removes a comment from the database.
    The function takes in an integer representing the id of the comment to be removed,
    and returns a dictionary containing information about that comment.

:param comment_id: int: Get the comment id from the url
:param db: Session: Get the database session
:param _: User: Get the current user
:return: The comment that was removed

    """
    comment = await repository_comments.remove_comment(comment_id, db)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such comment")
    return comment
