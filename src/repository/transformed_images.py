import cloudinary
from fastapi import Depends, HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.database.models import TransformedImage, Image, User, Role
from src.database.db import get_db
from src.schemas.transformed_image_schemas import TransformedImageModel
from src.services.transformed_image import create_transformations, generate_and_upload_qr_code
from src.conf.config import settings


cloudinary.config(
        cloud_name=settings.CLOUDINARY_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True
    )


async def create_transformed_picture(body: TransformedImageModel,
                                     current_user,
                                     image_id: int,
                                     db: Session = Depends(get_db)):
    """
The create_transformed_picture function takes in a TransformedImageModel object, the current user, and an image id.
It then queries the database for an Image with that id and checks if it belongs to the current user. If not, it raises a 404 error.
If so, it creates transformations from the TransformedImageModel object using create_transformations function (see above).
Then we use Cloudinary's build_url method to generate a new url for our transformed image based on those transformations.
We also generate and upload a QR code of this new url using our generate_and_upload_qr_code function (

:param body: TransformedImageModel: Get the transformation parameters from the request body
:param current_user: Get the user id from the token
:param image_id: int: Specify the image that will be transformed
:param db: Session: Access the database
:return: A transformedimage object

"""
    original_image = db.query(Image).filter(and_(Image.id == image_id, Image.user_id == current_user.id)).first()
    if not original_image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Original image not found")

    transformations = create_transformations(body)

    public_id = original_image.public_name
    file_name = public_id + "_" + str(current_user.username)
    new_url = cloudinary.CloudinaryImage(f'PhotoNet/{file_name}').build_url(transformation=transformations)
    qrcode_url = generate_and_upload_qr_code(new_url)
    print(qrcode_url)

    new_transformed_image = TransformedImage(transform_image_url=new_url, qrcode_image_url=qrcode_url,
                                             image_id=original_image.id)
    db.add(new_transformed_image)
    db.commit()
    db.refresh(new_transformed_image)
    return new_transformed_image


async def get_all_transformed_images(skip: int, limit: int, image_id: int, db: Session, current_user):
    """
The get_all_transformed_images function returns a list of all transformed images for the given image_id.
    The function takes in an integer skip, limit, and image_id as parameters.
    It also takes in a database session object and current user object from the fastapi security module.

:param skip: int: Skip a certain number of images in the database
:param limit: int: Limit the number of images returned
:param image_id: int: Filter the transformed images by image_id
:param db: Session: Access the database
:param current_user: Check if the user is owner of the image
:return: A list of transformed images for a given image

    """
    transformed_list = db.query(TransformedImage).join(Image). \
        filter(and_(TransformedImage.image_id == image_id, Image.user_id == current_user.id)). \
        offset(skip).limit(limit).all()
    if not transformed_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Transformed images for this image not found or user is not owner of this image")
    return transformed_list


async def get_transformed_img_by_id(transformed_id: int, db: Session, current_user):
    """
The get_transformed_img_by_id function is used to retrieve a transformed image from the database.
    It takes in an integer representing the id of the transformed image, and returns that transformed
    image if it exists in the database.

:param transformed_id: int: Get the transformed image by id
:param db: Session: Pass the database session to the function
:param current_user: Get the user_id of the current user
:return: A transformed image object

    """
    transformed_image = db.query(TransformedImage).join(Image). \
        filter(and_(TransformedImage.id == transformed_id, Image.user_id == current_user.id)).first()
    if not transformed_image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Transformed image not found or user is not owner of this image")
    return transformed_image


async def delete_transformed_image_by_id(transformed_id: int, db: Session, user):
    """
The delete_transformed_image_by_id function deletes a transformed image from the database.
    It takes in an integer representing the id of the transformed image to be deleted,
    and a Session object for interacting with the database. The function returns
    an HTTPException if it fails to delete or find a transformed image.

:param transformed_id: int: Specify the id of the transformed image to be deleted
:param db: Session: Access the database
:param user: Check the role of the user
:return: The deleted transformed image

    """
    if user.role == Role.admin:
        transformed_image = db.query(TransformedImage).join(Image). \
            filter(TransformedImage.id == transformed_id).first()
        if not transformed_image:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transformed image not found")
        db.delete(transformed_image)
        db.commit()
        return transformed_image
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the admin can delete this data")


async def get_qrcode_transformed_image_by_id(transformed_id: int, db: Session, current_user):
    """
The get_qrcode_transformed_image_by_id function returns the transformed image with the given id.
    The function takes in a transformed_id and a db Session object, and returns an Image object.

:param transformed_id: int: Get the transformed image by id
:param db: Session: Access the database
:param current_user: Check if the user is the owner of this image
:return: The transformed image with the given id

    """
    transformed_image = db.query(TransformedImage).join(Image). \
        filter(and_(TransformedImage.id == transformed_id, Image.user_id == current_user.id)).first()
    if not transformed_image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Transformed image not found or user is not owner of this image")
    print(transformed_image.qrcode_image_url)
    return transformed_image


async def get_url_transformed_image_by_id(transformed_id: int, db: Session, current_user):
    """
The get_url_transformed_image_by_id function returns the transformed image url by id.
    Args:
        transformed_id (int): The id of the transformed image to be returned.
        db (Session): The database session object used for querying and updating data in the database.
            This is injected into this function by FastAPI when it calls this function, so you don't need to pass it in yourself!

:param transformed_id: int: Find the transformed image in the database
:param db: Session: Access the database
:param current_user: Get the user id of the current user
:return: The transformed image object with the given id

    """
    transformed_image = db.query(TransformedImage).join(Image). \
        filter(and_(TransformedImage.id == transformed_id, Image.user_id == current_user.id)).first()
    if not transformed_image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Transformed image not found or user is not owner of this image")
    return transformed_image
