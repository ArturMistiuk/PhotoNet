from sqlalchemy.orm import Session

from src.database.models import Comment, Image
from src.schemas.comment_schemas import CommentModel


async def get_comments(db: Session):
    """
    The function get_comments returns all comments in the database.

    :param db: Session: passes the database session to the function
    :return: All comments from the database.
    """
    return db.query(Comment).all()


async def get_comment_by_id(comment_id: int, db: Session):
    """
    The function get_comment_by_id returns a comment object from the database based on its identifier.

    :param comment_id: int: filter the database for a specific comment
    :param db: Session: passes the database session to the function
    :return: Comment object
    """
    return db.query(Comment).filter_by(id=comment_id).first()


async def create_comment(body: CommentModel, db: Session):
    """
    The function create_comment creates a new comment in the database.

    :param body: CommentModel: pass the data to create a new comment
    :param db: Session: passes the database session to the function
    :return: Comment object
    """
    comment = Comment(**body.dict())
    db.add(comment)
    db.commit()
    return comment


async def update_comment(body: CommentModel, comment_id, db: Session):
    """
    The function update_comment updates a comment in the database.

    :param body: CommentModel: pass the updated comment to the function
    :param comment_id: get the comment from the database
    :param db: Session: passes the database session to the function
    :return: Comment object
     """
    comment = await get_comment_by_id(comment_id, db)
    if comment:
        comment.comment = body.comment
        db.commit()
    return comment


async def remove_comment(comment_id, db: Session):
    """
    The function remove_comment deletes a comment from the database.

    :param comment_id: Find the comment to be deleted.
    :param db: Session: passes the database session to the function
    :return: The deleted 'Comment' object.
    """
    comment = await get_comment_by_id(comment_id, db)
    if comment:
        db.delete(comment)
        db.commit()
    return comment


async def get_image_by_id(image_id: int, db: Session):
    """
    The function get_image_by_id takes image_id and a database session, and returns an Image object with that identifier. If such an image does not exist, it returns None.

    :param image_id: int: Specify the identifier of the image to retrieve
    :param db: Session: passes the database session to the function
    :return: Image or None: Image with the specified identifier or None if not found.
    """
    image = db.query(Image).filter_by(id=image_id).first()
    return image
