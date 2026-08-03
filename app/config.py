from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    database_url: str
    redis_url: str
    base_url: str

    model_config = {"env_file": ".env", "extra": "ignore"}

settings = Settings()