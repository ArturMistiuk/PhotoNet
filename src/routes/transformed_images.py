from typing import List

from fastapi import APIRouter, Path, status, Depends
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.routes.tags import access_get, access_delete, access_create
from src.schemas.transformed_image_schemas import TransformedImageModel, TransformedImageResponse, \
    UrlTransformedImageResponse, UrlQRCodeTransformedImageResponse
from src.repository.transformed_images import get_all_transformed_images, delete_transformed_image_by_id, \
    create_transformed_picture, get_qrcode_transformed_image_by_id, get_transformed_img_by_id, \
    get_url_transformed_image_by_id
from src.services.auth import auth_service

router = APIRouter(prefix="/transformed_images", tags=["transformed images"])


@router.post("/{image_id}", response_model=TransformedImageResponse,
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(access_create)])
async def create_new_transformed_image(body: TransformedImageModel,
                                       user: User = Depends(auth_service.get_current_user),
                                       image_id: int = Path(ge=1),
                                       db: Session = Depends(get_db), ):
    """
The create_new_transformed_image function creates a new transformed image.
    The function takes in the following parameters:
        body (TransformedImageModel): A TransformedImageModel object containing the information for the new transformed image.
        user (User): A User object containing information about the current user. This is obtained from auth_service's get_current_user function, which uses JWT to authenticate users and obtain their info from our database.
        image_id (int): An integer representing an existing Image's ID number in our database that we want to transform into a new TransformedImage using this endpoint call.

:param body: TransformedImageModel: Get the data from the request body
:param user: User: Get the current user
:param image_id: int: Get the image id from the path
:param db: Session: Get the database session
:param : Get the id of the image that is being transformed
:return: A new transformed image

    """
    new_transformed_picture = await create_transformed_picture(body, user, image_id, db)
    return new_transformed_picture


@router.get("/{image_id}", response_model=List[TransformedImageResponse], dependencies=[Depends(access_get)])
async def get_all_transformed_images_for_original_image_by_id(skip: int = 0, limit: int = 10,
                                                              image_id: int = Path(ge=1),
                                                              db: Session = Depends(get_db),
                                                              user: User = Depends(auth_service.get_current_user)):
    """
The get_all_transformed_images_for_original_image_by_id function returns a list of all transformed images for the original image with the given id.

:param skip: int: Specify the number of images to skip
:param limit: int: Limit the number of images returned
:param image_id: int: Specify the id of the original image that we want to get all transformed images for
:param db: Session: Access the database
:param user: User: Check if the user is logged in
:return: All the transformed images for a given

    """
    images = await get_all_transformed_images(skip, limit, image_id, db, user)
    return images


@router.get("/transformed/{transformed_image_id}", response_model=TransformedImageResponse,
            dependencies=[Depends(access_get)])
async def get_transformed_images_by_image_id(transformed_image_id: int = Path(ge=1),
                                             db: Session = Depends(get_db),
                                             user: User = Depends(auth_service.get_current_user)):
    """
The get_transformed_images_by_image_id function returns a transformed image by its ID.

:param transformed_image_id: int: Specify the id of the transformed image that we want to get
:param db: Session: Get the database session
:param user: User: Check if the user is authenticated, and to get the current user's id
:return: A transformed image by its id

    """
    transformed_image = await get_transformed_img_by_id(transformed_image_id, db, user)
    return transformed_image


@router.get("/transformed/{transformed_image_id}/qrcode", response_model=UrlQRCodeTransformedImageResponse,
            dependencies=[Depends(access_get)])
async def get_qrcode_for_transformed_image(transformed_image_id: int = Path(ge=1),
                                           db: Session = Depends(get_db),
                                           user: User = Depends(auth_service.get_current_user)):
    """
The get_qrcode_for_transformed_image function returns the qrcode for a given transformed image.
    The function takes in an integer representing the id of a transformed image and returns that
    transformed image's qrcode.

:param transformed_image_id: int: Get the transformed image by id
:param db: Session: Get the database session
:param user: User: Check if the user is authenticated
:return: The transformed image with the given id

    """
    transformed_image = await get_qrcode_transformed_image_by_id(transformed_image_id, db, user)
    return transformed_image


@router.get("/transformed/{transformed_image_id}/url", response_model=UrlTransformedImageResponse,
            dependencies=[Depends(access_get)])
async def get_url_for_transformed_image(transformed_image_id: int = Path(ge=1),
                                        db: Session = Depends(get_db),
                                        user: User = Depends(auth_service.get_current_user)):
    """
The get_url_for_transformed_image function returns the URL for a transformed image.

:param transformed_image_id: int: Get the id of the transformed image
:param db: Session: Access the database
:param user: User: Get the current user
:return: The url for the transformed image

    """
    transformed_image = await get_url_transformed_image_by_id(transformed_image_id, db, user)
    return transformed_image


@router.delete("/transformed/{transformed_image_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(access_delete)])
async def delete_transformed_image(transformed_image_id: int = Path(ge=1),
                                   db: Session = Depends(get_db),
                                   user: User = Depends(auth_service.get_current_user)):
    """
The delete_transformed_image function deletes a transformed image from the database.

:param transformed_image_id: int: Get the id of the transformed image to be deleted
:param db: Session: Get the database session
:param user: User: Check if the user is authenticated
:return: None

    """
    transformed_image = await delete_transformed_image_by_id(transformed_image_id, db, user)
    return None
