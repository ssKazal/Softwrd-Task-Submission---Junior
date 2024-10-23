import os
from pydantic_settings import BaseSettings

# Define the path to the .env file relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE_PATH = os.path.join(BASE_DIR, "..", ".env")


class Settings(BaseSettings):
    database_url: str
    mongo_initdb_database: str

    class Config:
        env_file = ENV_FILE_PATH
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
