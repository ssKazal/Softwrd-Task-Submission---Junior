from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    mongo_initdb_database: str

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
