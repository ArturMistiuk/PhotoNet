from collections import OrderedDict

from fastapi import HTTPException, status

from src.database.models import Image
from src.schemas.image_schemas import ImageAddModel


async def images_service_change_name(public_name, db):
    """
The images_service_change_name function is used to change the name of an image.
    It takes in a public_name and db as parameters, and returns a correct_public_name.
    The function checks if the public name already exists in the database,
    if it does then it adds a suffix to make sure that there are no duplicate names.

:param public_name: Check if the public name already exists in the database
:param db: Access the database
:return: A correct public name for the image

    """
    correct_public_name = public_name
    suffix = 1

    while db.query(Image).filter(Image.public_name == correct_public_name).first():
        suffix += 1
        correct_public_name = f"{public_name}_{suffix}"

    return correct_public_name


async def images_service_normalize_tags(body):
    """
The images_service_normalize_tags function takes a list of tags and returns a list of normalized tags.
    Normalized means that the tag is stripped, lowercased, and truncated to 25 characters.
    The function also removes duplicate tags from the list.

:param body: Get the tags from the request body
:return: A list of strings

    """
    tags = [tag[:25].strip() for tag_str in body.tags for tag in tag_str.split(",") if tag]
    correct_tags = list(OrderedDict.fromkeys(tags))
    return correct_tags
