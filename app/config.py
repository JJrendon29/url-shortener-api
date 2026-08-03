from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_USER : str
    POSTGRES_PASSWORD : str
    POSTGRES_DB : str
    DATABASE_URL : str
    REDIS_URL : str
    BASE_URL : str
    
    model_config = {"env_file": ".env", "extra": "ignore"}

# Esta línea crea una instancia única que importás desde cualquier parte
settings = Settings()