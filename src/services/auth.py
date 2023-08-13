
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.conf.messages import AuthMessages
from src.database.db import get_db
from src.repository import users as repository_users


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.JWT_SECRET_KEY
    ALGORITHM = settings.JWT_ALGORITHM
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

    def verify_password(self, plain_password, hashed_password):
        """
    The verify_password function takes a plain-text password and hashed password as arguments.
    It then uses the pwd_context object to verify that the plain-text password matches the hashed one.

    :param self: Represent the instance of the class
    :param plain_password: Pass in the password that is entered by the user
    :param hashed_password: Compare the password that is stored in the database with the password that is entered by a user
    :return: True if the password is correct and false otherwise
    
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
    The get_password_hash function takes a password as an argument and returns the hashed version of that password.
    The hash is generated using the pwd_context object's hash method, which uses bcrypt to generate a secure hash.

    :param self: Represent the instance of the class
    :param password: str: Pass in the password that is being hashed
    :return: A password hash
    
        """
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
    The create_access_token function creates a new access token.
        Args:
            data (dict): A dictionary of key-value pairs to include in the JWT payload.
            expires_delta (Optional[float]): An optional expiration time, in seconds, for the access token. Defaults to 60 minutes if not provided.

    :param self: Access the class variables and methods
    :param data: dict: Pass the data that will be encoded in the jwt
    :param expires_delta: Optional[float]: Set the expiration time of the access token
    :return: A token that is encoded with the data,
        
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=60)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
    The create_refresh_token function creates a refresh token for the user.
        Args:
            data (dict): A dictionary containing the user's id and username.
            expires_delta (Optional[float]): The number of seconds until the refresh token expires. Defaults to None, which sets it to 7 days from now.

    :param self: Access the attributes and methods of a class
    :param data: dict: Pass the user's id, username and email to the function
    :param expires_delta: Optional[float]: Set the expiration time of the refresh token
    :return: A refresh token
    
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
    The decode_refresh_token function is used to decode the refresh token.
        The function will raise an HTTPException if the refresh token is invalid or expired.
        If successful, it will return a string containing the email of the user who owns this refresh_token.

    :param self: Represent the instance of the class
    :param refresh_token: str: Pass the refresh token to the function
    :return: The email of the user that is associated with the refresh token
    
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=AuthMessages.invalid_scope_for_token)
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail=AuthMessages.could_not_validate_credentials)

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
    The get_current_user function is a dependency that will be used in the
        protected endpoints. It takes a token as an argument and returns the user
        if it's valid, or raises an HTTPException with status code 401 if not.

    :param self: Represent the instance of the class
    :param token: str: Get the token from the request header
    :param db: Session: Get the database session
    :return: The user object that is stored in the database
    
    """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AuthMessages.could_not_validate_credentials,
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception
     
        user = await repository_users.get_user_by_email(email, db)

        return user

    def create_email_token(self, data: dict):
        """
    The create_email_token function takes a dictionary of data and returns a token.
    The token is created using the JWT library, which uses the SECRET_KEY and ALGORITHM to create an encoded string.
    The data dictionary contains information about the user's email address, username, password reset code (if applicable),
    and expiration date for the token.

    :param self: Represent the instance of the class
    :param data: dict: Pass in a dictionary of data that will be encoded
    :return: A token that is encoded using a secret key and an algorithm
    
    """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=1)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """
    The get_email_from_token function takes a token as an argument and returns the email address associated with that token.
    The function uses the jwt library to decode the token, which is then used to return the email address.

    :param self: Represent the instance of the class
    :param token: str: Pass the token that is sent to the user's email address
    :return: The email address that was passed to the create_access_token function
    
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail=AuthMessages.invalid_token_for_email_verification)


auth_service = Auth()
