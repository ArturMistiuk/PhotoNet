from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.database.models import Image, User, Tag, Comment, Role
from src.repository.ratings import get_average_rating
from src.schemas.image_schemas import ImageUpdateModel, ImageAddModel, ImageAddTagModel
from src.services.images import images_service_normalize_tags


async def get_images(db: Session, user: User):
    """
    The function get_images returns a list of images along with their associated ratings and comments.
    If the user is an administrator, all images are returned. Otherwise, only the user's own images are returned.

    :param db: Session: passes the database session to the function
    :param user: User: Specify whether the user is an administrator or a regular user
    :return: List of dictionaries, each dictionary containing an image object and its associated ratings and comments.
    """
    # if user.role == Role.admin:
    # images = db.query(Image).filter(Image.id == id).first()
    # else:
    images = db.query(Image).order_by(Image.id).all()
    user_response = []
    for image in images:
        ratings = await get_average_rating(image.id, db)
        comments = db.query(Comment).filter(Comment.image_id == image.id, Comment.user_id == user.id).all()
        user_response.append({"image": image, "ratings": ratings, "comments": comments})
    return user_response


async def get_image(db: Session, id: int, user: User):
    """
    The function get_image takes a database session, an image identifier, and a user.
    If the user is an administrator, it returns the image with that identifier from the database.
    Otherwise, it returns only the image with that identifier that belongs to this user.

    :param db: Session: to access the database
    :param id: int: Specify the identifier of the image being requested
    :param user: User: Check if the user is an administrator
    :return: Tuple with the image, ratings, and comments.
    """
     # if user.role == Role.admin:
     # images = db.query(Image).filter(Image.id == id).first()
     # else:
    image = db.query(Image).filter(Image.id == id).first()

    if image:
        ratings = await get_average_rating(image.id, db)
        comments = db.query(Comment).filter(Comment.image_id == image.id, Comment.user_id == user.id).all()
        return image, ratings, comments
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")


async def admin_get_image(db: Session, user_id: id):
    """
    The function admin_get_image is used to retrieve all images for a specific user.
        The function takes a database session and the user_id of the desired user.
        Then it queries all images with this particular identifier, sorts them by identifier, and returns them as an array of objects.

    :param db: Session: connection to the database
    :param user_id: id: get images for a specific user
    :return: All images in the database for the specified user.
    """
    images = db.query(Image).filter(Image.user_id == user_id).order_by(Image.id).all()
    if images:
        user_response = []
        for image in images:
            ratings = await get_average_rating(image.id, db)
            comments = db.query(Comment).filter(Comment.image_id == image.id, Comment.user_id == image.user_id).all()
            user_response.append({"image": image, "ratings": ratings, "comments": comments})
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    return user_response


async def add_image(db: Session, image: ImageAddModel, tags: list[str], url: str, public_name: str, user: User):
    """
    The function add_image adds an image to the database.

    :param tags: list[str]
    :param db: Session: access to the database
    :param image: ImageAddModel: get the description of the image
    :param url: str: save the URL of the image
    :param public_name: str: Save the name of the image in the database
    :param user: User: get the user identifier from the database
    :return: Tuple with two elements: image and string.
    """
    if not user:
        return None

    detail = ""
    num_tags = 0
    image_tags = []
    for tag in tags:
        if len(tag) > 25:
            tag = tag[0:25]
        if not db.query(Tag).filter(Tag.name == tag.lower()).first():
            db_tag = Tag(name=tag.lower())
            db.add(db_tag)
            db.commit()
            db.refresh(db_tag)
        if num_tags < 5:
            image_tags.append(tag.lower())
        num_tags += 1

    if num_tags >= 5:
        detail = " But be attentive you can add only five tags to an image"

    tags = db.query(Tag).filter(Tag.name.in_(image_tags)).all()
    # Save image to database
    db_image = Image(description=image.description, tags=tags, url=url, public_name=public_name, user_id=user.id)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image, detail


async def update_image(db: Session, image_id, image: ImageUpdateModel, user: User):
    """
    The function update_image updates the description of an image in the database.

    :param db: Session: access to the database
    :param image_id: int: Find the image in the database
    :param image: ImageUpdateModel: pass the image update model
    :param user: User: Check if the user is an administrator
    :return: db_image
    """
    if user.role == Role.admin:
        db_image = db.query(Image).filter(Image.id == image_id).first()
    else:
        db_image = db.query(Image).filter(Image.id == image_id, Image.user_id == user.id).first()

    if db_image:
        db_image.description = image.description
        db.commit()
        db.refresh(db_image)
        return db_image
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")


async def add_tag(db: Session, image_id, body: ImageAddTagModel, user: User):
    """
    The function add_tag adds tags to an image.

    :param db: Session: access to the database
    :param image_id: int: Specify the image to which the tags are added
    :param body: ImageAddTagModel: get the tags from the request body
    :param user: User: Check if the user is an administrator
    :return: Image object with updated tags
    """
    tags = await images_service_normalize_tags(body)

    detail = ""
    num_tags = 0
    image_tags = []
    for tag in tags:
        if tag:
            if len(tag) > 25:
                tag = tag[0:25]
            if not db.query(Tag).filter(Tag.name == tag.lower()).first():
                db_tag = Tag(name=tag.lower())
                db.add(db_tag)
                db.commit()
                db.refresh(db_tag)
            if num_tags < 5:
                image_tags.append(tag.lower())
            num_tags += 1

    if num_tags >= 5:
        detail = "But be attentive you can add only five tags to an image"

    tags = db.query(Tag).filter(Tag.name.in_(image_tags)).all()

    if user.role == Role.admin:
        image = db.query(Image).filter(Image.id == image_id).first()
    else:
        image = db.query(Image).filter(Image.id == image_id, Image.user_id == user.id).first()

    if image:
        image.updated_at = datetime.utcnow()
        image.tags = tags
        db.commit()
        db.refresh(image)
        return image, detail
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")


async def delete_image(db: Session, id: int, user: User):
    """
    The function delete_image deletes an image from the database.

    :param db: Session: access to the database
    :param id: int: Specify the identifier of the image to be deleted
    :param user: User: Check if the user is an administrator
    :return: The deleted image
    """
    if user.role == Role.admin:
        db_image = db.query(Image).filter(Image.id == id).first()
    else:
        db_image = db.query(Image).filter(Image.id == id, Image.user_id == user.id).first()

    if db_image:
        db.delete(db_image)
        db.commit()
        return db_image
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
