import os

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from src.database.db import get_db
from src.database.models import User, Role
from src.schemas.image_schemas import ImageAddResponse, ImageUpdateModel, ImageAddModel, ImageAddTagResponse, \
    ImageAddTagModel, ImageGetAllResponse, ImageGetResponse, ImageDeleteResponse, ImageUpdateDescrResponse, \
    ImageAdminGetAllResponse
from src.repository import images
from src.services.auth import auth_service
from src.services.images import images_service_change_name, images_service_normalize_tags
from src.services.roles import RolesAccess

load_dotenv()

router = APIRouter(prefix='/images', tags=["images"])

access_all = RolesAccess([Role.admin, Role.moderator, Role.user])
access_admin = RolesAccess([Role.admin])


@router.get("", response_model=ImageGetAllResponse, dependencies=[Depends(access_all)])
async def get_images(db: Session = Depends(get_db),
                     current_user: User = Depends(auth_service.get_current_user)):
    """
The get_images function returns a list of images for the current user.

:param db: Session: Pass the database session to the function
:param current_user: User: Get the current user
:return: A list of images that are associated with the current user

    """
    user_images = await images.get_images(db, current_user)
    return {"images": user_images}


@router.get("/image_id/{id}", response_model=ImageGetResponse, dependencies=[Depends(access_all)])
async def get_image(id: int, db: Session = Depends(get_db),
                    current_user: User = Depends(auth_service.get_current_user)):
    """
The get_image function returns a single image with its ratings and comments.

:param id: int: Specify the id of the image that is being requested
:param db: Session: Pass the database session to the get_image function
:param current_user: User: Get the current user from the database
:return: The image, the ratings and the comments

    """
    user_image, ratings, comments = await images.get_image(db, id, current_user)
    return {"image": user_image, "ratings": ratings, "comments": comments}


@router.get("/user_id/{user_id}", response_model=ImageAdminGetAllResponse, dependencies=[Depends(access_admin)])
async def admin_get_images(user_id: int, db: Session = Depends(get_db),
                           current_user: User = Depends(auth_service.get_current_user)):
    """
The admin_get_images function is used to get all images for a user.
    This function requires the user_id of the user whose images you want to retrieve.
    The current_user must be an admin in order to use this function.

:param user_id: int: Get the images of a specific user
:param db: Session: Access the database
:param current_user: User: Get the current user who is making the request
:return: A list of all images in the database

    """
    user_response = await images.admin_get_image(db, user_id)
    return {"images": user_response}


@router.post("/add", response_model=ImageAddResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(access_all)])
async def upload_image(body: ImageAddModel = Depends(), file: UploadFile = File(), db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
The upload_image function is used to upload an image to the database.
    The function takes in a body, file, db, and current_user as parameters.
    The body parameter is used for the ImageAddModel class which contains all of the information needed for adding an image.
    The file parameter is used for uploading a file from your computer or device that you want to add as an image on PhotoNet.
        This will be uploaded using Cloudinary's API and stored there until it needs to be retrieved by another user viewing your profile page or gallery page.

:param body: ImageAddModel: Get the image's title, description and tags from the request body
:param file: UploadFile: Get the file from the request body
:param db: Session: Get the database session
:param current_user: User: Get the current user from the database
:return: The image and the details of the image

    """
    cloudinary.config(
            cloud_name=os.environ.get('CLOUDINARY_NAME'),
            api_key=os.environ.get('CLOUDINARY_API_KEY'),
            api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
            secure=True
        )

    correct_tags = await images_service_normalize_tags(body)

    public_name = file.filename.split(".")[0]

    correct_public_name = await images_service_change_name(public_name, db)

    file_name = correct_public_name + "_" + str(current_user.username)
    r = cloudinary.uploader.upload(file.file, public_id=f'PhotoNet/{file_name}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'PhotoNet/{file_name}') \
        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    image, details = await images.add_image(db, body, correct_tags, src_url, correct_public_name, current_user)

    return {"image": image, "detail": "Image was successfully added." + details}


@router.put("/update_description/{image_id}", response_model=ImageUpdateDescrResponse,
            dependencies=[Depends(access_all)])
async def update_description(image_id: int, image_info: ImageUpdateModel, db: Session = Depends(get_db),
                             current_user: User = Depends(auth_service.get_current_user)):
    """
The update_description function updates the description of an image.
    Args:
        image_id (int): The id of the image to be updated.
        db (Session, optional): SQLAlchemy Session. Defaults to Depends(get_db).
        current_user (User, optional): User object for currently logged in user. Defaults to Depends(auth_service.get_current_user).

:param image_id: int: Identify the image to be updated
:param image_info: ImageUpdateModel: Get the description of the image
:param db: Session: Get the database session
:param current_user: User: Get the user who is currently logged in
:return: A dictionary with the id, description and detail of the image

    """
    user_image = await images.update_image(db, image_id, image_info, current_user)
    return {"id": user_image.id, "description": user_image.description, "detail": "Image was successfully updated"}


@router.put("/update_tags/{image_id}", response_model=ImageAddTagResponse, dependencies=[Depends(access_all)])
async def add_tag(image_id, body: ImageAddTagModel = Depends(), db: Session = Depends(get_db),
                  current_user: User = Depends(auth_service.get_current_user)):
    """
The add_tag function adds a tag to an image.
    The function takes in the following parameters:
        - image_id: The id of the image that is being tagged.
        - body: A JSON object containing the tag name and value, as well as a description of what it means.

:param image_id: Identify the image to be updated
:param body: ImageAddTagModel: Validate the request body
:param db: Session: Get the database session
:param current_user: User: Get the user information from the token
:return: A dictionary with the updated image id, tags and a detail message

    """
    image, details = await images.add_tag(db, image_id, body, current_user)
    return {"id": image.id, "tags": image.tags, "detail": "Image was successfully updated." + details}


@router.delete("/{id}", response_model=ImageDeleteResponse, dependencies=[Depends(access_all)])
async def delete_image(id: int, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
The delete_image function deletes an image from the database.
    The function takes in a user_id and an image_id, and returns a dictionary with the deleted image's information.

:param id: int: Specify the id of the image that is to be deleted
:param db: Session: Get the database session
:param current_user: User: Get the current user from the database
:return: A dictionary with the deleted image and a message

    """
    user_image = await images.delete_image(db, id, current_user)
    return {"image": user_image, "detail": "Image was successfully deleted"}
