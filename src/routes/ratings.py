from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User, Role
from src.schemas.rating_schemas import RatingModel, RatingResponse, AverageRatingResponse
from src.repository import ratings as repository_ratings
from src.conf.messages import AuthMessages

from src.services.auth import auth_service
from src.services.roles import RolesAccess

router = APIRouter(prefix='/ratings', tags=["ratings"])

access_get = RolesAccess([Role.admin, Role.moderator, Role.user])
access_create = RolesAccess([Role.admin, Role.moderator, Role.user])
access_update = RolesAccess([Role.admin, Role.moderator])
access_delete = RolesAccess([Role.admin, Role.moderator])


@router.get("/image/{image_id}", response_model=float, dependencies=[Depends(access_get)])
async def common_image_rating(image_id, _: User = Depends(auth_service.get_current_user),
                              db: Session = Depends(get_db)):
    """
The common_image_rating function returns the average rating of an image.
    ---
    get:
      summary: Get the average rating of an image.
      description: Returns a JSON object containing the average rating for a given image ID.  The user must be logged in to access this endpoint, and must have rated that particular image before they can view its common_image_rating value.

:param image_id: Get the image from the database
:param _: User: Get the current user from the auth_service
:param db: Session: Access the database
:return: The average rating of the image with id = image_id

    """
    common_rating = await repository_ratings.get_average_rating(image_id, db)
    return common_rating


@router.get("/{rating_id}", response_model=RatingResponse, dependencies=[Depends(access_get)])
async def read_rating(rating_id: int, _: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """
The read_rating function is used to read a single rating from the database.
It takes in an integer representing the ID of the rating, and returns a Rating object.

:param rating_id: int: Specify the rating that is being updated
:param _: User: Tell fastapi that the user is not needed for this function
:param db: Session: Pass the database session to the repository
:return: A rating object

    """
    rating = await repository_ratings.get_rating(rating_id, db)
    if rating is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
    return rating


@router.post("/{image_id}", response_model=RatingResponse, dependencies=[Depends(access_create)])
async def create_rate(image_id, body: RatingModel, current_user: User = Depends(auth_service.get_current_user),
                      db: Session = Depends(get_db)):
    """
The create_rate function creates a new rating for an image.
    The function takes the following parameters:
        - image_id: The id of the image to be rated.
        - body: A RatingModel object containing all information about the rating, including user_id and value.
                This is passed in as JSON data in a POST request to /ratings/{image_id}.

:param image_id: Get the image from the database
:param body: RatingModel: Get the rating value from the request body
:param current_user: User: Get the current user from the database
:param db: Session: Get the database session
:return: A ratingmodel object

    """
    rating = await repository_ratings.create_rating(image_id, body, current_user, db)
    if rating is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Please, check the image_id. You can't rate your images or give 2 or more rates for 1 image")
    return rating


@router.put("/{rating_id}", response_model=RatingResponse, dependencies=[Depends(access_update)])
async def update_rating(body: RatingModel, rating_id: int, db: Session = Depends(get_db),
                        _: User = Depends(auth_service.get_current_user)):
    """
The update_rating function updates a rating in the database.
    The function takes an id of the rating to update, and a body containing all fields that need updating.
    If no user is logged in, or if the user does not have permission to update ratings,
    then an HTTPException will be raised with status code 401 (Unauthorized).

:param body: RatingModel: Get the request body from the client
:param rating_id: int: Get the rating id from the url
:param db: Session: Get the database session from the dependency injection container
:param _: User: Check if the user is logged in
:return: A ratingmodel object

    """
    rating = await repository_ratings.update_rating(rating_id, body, db)
    if rating is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Rating not found or you can't update the rating because of rules or roles")
    return rating


@router.delete("/{rating_id}", response_model=RatingResponse, dependencies=[Depends(access_delete)])
async def remove_rating(rating_id: int, db: Session = Depends(get_db),
                        _: User = Depends(auth_service.get_current_user)):
    """
The remove_rating function removes a rating from the database.
    It takes in an integer representing the id of the rating to be removed, and returns a dictionary containing information about that rating.
    If no such rating exists, it raises an HTTPException with status code 404.

:param rating_id: int: Specify the id of the rating to be deleted
:param db: Session: Pass the database session to the repository
:param _: User: Check if the user is logged in
:return: A rating object

    """
    rating = await repository_ratings.remove_rating(rating_id, db)
    if rating is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Rating not found or you don't have enough rules to delete")
    return rating
