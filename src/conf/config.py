from pydantic_settings import BaseSettings    # PydanticUserError
from pydantic import EmailStr


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    REDIS_HOST: str
    REDIS_PORT: int
    CLOUDINARY_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    DB_USER: str
    DB_PASSWORD: str
    DB_DOMAIN: str
    DB_NAME: str
    DB_PORT: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
