from typing import List, Type

from sqlalchemy.orm import Session

from src.database.models import Tag
from src.schemas.tag_schemas import TagModel


async def get_tags(skip: int, limit: int, db: Session) -> List[Type[Tag]]:
    """
The get_tags function returns a list of tags from the database.

:param skip: int: Skip the first n tags in the database
:param limit: int: Specify the number of items to return
:param db: Session: Pass the database session to the function
:return: A list of tag objects
    """
    return db.query(Tag).offset(skip).limit(limit).all()


async def get_tag(tag_id: int, db: Session) -> Type[Tag] | None:
    """
The get_tag function returns a Tag object from the database, given its ID.

:param tag_id: int: Specify the id of the tag to be retrieved
:param db: Session: Pass the database session to the function
:return: The tag object with the given id
    """
    return db.query(Tag).filter(Tag.id == tag_id).first()


async def create_tag(body: TagModel, db: Session) -> Tag:
    """
The create_tag function creates a new tag in the database.

:param body: TagModel: Pass the data from the request body into the function
:param db: Session: Access the database
:return: A tag object
    """
    tag = Tag(name=body.name.lower())
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


async def update_tag(tag_id: int, body: TagModel, db: Session) -> Tag | None:
    """
The update_tag function updates a tag in the database.
    Args:
        tag_id (int): The id of the tag to update.
        body (TagModel): The new name for the updated Tag object.

:param tag_id: int: Find the tag in the database
:param body: TagModel: Get the new name of the tag
:param db: Session: Access the database
:return: A tag object if the tag was updated successfully, otherwise it returns none

    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag:
        new_tag_name_in_base = db.query(Tag).filter(Tag.name == body.name.lower()).first()
        if new_tag_name_in_base:
            return None
        tag.name = body.name.lower()
        db.commit()
    return tag


async def remove_tag(tag_id: int, db: Session) -> Tag | None:
    """
The remove_tag function removes a tag from the database.
    Args:
        tag_id (int): The id of the tag to be removed.
        db (Session): A connection to the database.

:param tag_id: int: Get the tag from the database
:param db: Session: Pass the database session to the function
:return: The tag that was removed from the database

    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag:
        db.delete(tag)
        db.commit()
    return tag


async def remove_tag(tag_id: int, db: Session) -> Tag | None:
    """
The remove_tag function removes a tag from the database.
    Args:
        tag_id (int): The id of the tag to be removed.
        db (Session): A connection to the database.

:param tag_id: int: Specify the tag to be removed
:param db: Session: Pass in the database session
:return: The removed tag or none if the tag doesn't exist

    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag:
        db.delete(tag)
        db.commit()
    return tag


async def get_tag_by_name(tag_name: str, db: Session) -> Tag | None:
    """
The get_tag_by_name function takes in a tag name and returns the corresponding Tag object from the database.
If no such tag exists, it returns None.

:param tag_name: str: Specify the name of the tag that we want to get
:param db: Session: Pass the database session to the function
:return: A tag object

    """
    tag = db.query(Tag).filter(Tag.name == tag_name.lower()).first()
    return tag
