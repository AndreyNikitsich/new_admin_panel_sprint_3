from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseSettings):
    dbname: str
    user: str
    host: str
    port: str
    password: str
    options: str = "-c search_path=content"

    model_config = SettingsConfigDict(env_file="../.env", env_prefix="POSTGRES_")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env")

@lru_cache
def db_settings():
    return PostgresSettings()

@lru_cache
def global_settings():
    return Settings()
