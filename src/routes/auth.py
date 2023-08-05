from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import users as repository_users
from src.schemas.user_schemas import UserModel, UserResponse
from src.schemas.auth_schemas import TokenModel, RequestEmail
from src.services.auth import auth_service
from src.services.email import send_email
from src.conf.messages import AuthMessages

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
The signup function creates a new user in the database.
    It takes a UserModel object as input, which contains the following fields:
        - username (str)
        - email (str)
        - password (str)

:param body: UserModel: Get the data from the request body
:param background_tasks: BackgroundTasks: Add a task to the background tasks queue
:param request: Request: Get the base url of the server
:param db: Session: Get the database session
:return: A usermodel object

    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=AuthMessages.account_already_exists)
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
The login function is used to authenticate a user.
    It takes the username and password from the request body,
    verifies them against the database, and returns an access token if successful.

:param body: OAuth2PasswordRequestForm: Get the username and password from the request body
:param db: Session: Get access to the database
:return: A jwt token and a refresh_token

    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=AuthMessages.invalid_email)
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=AuthMessages.email_not_confirmed)
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=AuthMessages.invalid_password)
    if user.banned:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=AuthMessages.banned)
    # Генерувати JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
The refresh_token function is used to refresh the access token.
    The function takes in a refresh token and returns an access_token, a new refresh_token, and the type of token.
    If the user's account has been banned or if they have logged out then this function will not work.

:param credentials: HTTPAuthorizationCredentials: Get the token from the request header
:param db: Session: Pass the database session to the function
:return: A json object with the access_token, refresh_token and token_type

    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=AuthMessages.invalid_refresh_token)
    if user.banned:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=AuthMessages.banned)

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
The confirmed_email function is used to confirm a user's email address.
    It takes in the token that was sent to the user's email and uses it to get their email address.
    Then, it gets the user from our database using their email address and checks if they exist.
    If they don't exist, we return an error message saying that there was an error verifying their account.
    If they do exist, we check if their account has already been confirmed or not by checking if confirmed is True or False for them in our database (True means verified).
    If it has already been verified, then

:param token: str: Get the token from the url
:param db: Session: Get the database connection
:return: A message if the email is already confirmed

"""
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=AuthMessages.verification_error)
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    """
The request_email function is used to send an email to the user with a link that will allow them
to confirm their email address. The function takes in a RequestEmail object, which contains the
email of the user who wants to confirm their account. It then checks if there is already a confirmed
user with that email address, and if so returns an error message saying as much. If not, it sends
an email containing a confirmation link.

:param body: RequestEmail: Pass the email address to be confirmed
:param background_tasks: BackgroundTasks: Add a task to the background tasks queue
:param request: Request: Get the base_url of the application
:param db: Session: Access the database
:return: A message to the user

    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": AuthMessages.your_email_is_already_confirmed}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": AuthMessages.check_your_email_for_confirmation}
