import os
from functools import cached_property

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR_PATH = os.path.dirname(os.path.abspath(__file__))


class PostgresSettings(BaseSettings):
    dbname: str
    user: str
    host: str
    port: str
    password: str
    options: str = "-c search_path=content"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="POSTGRES_")


class ElasticSettings(BaseSettings):
    host: str
    port: str
    connection_schema: str
    index_name: str
    index_file_name: str = "index_config.json"

    @cached_property
    def url(self):
        return f"{self.connection_schema}://{self.host}:{self.port}"

    @cached_property
    def index_file_path(self):
        return BASE_DIR_PATH / self.index_file_name

    model_config = SettingsConfigDict(env_file=".env", env_prefix="ELASTIC_")


class OthersSettings(BaseSettings):
    etl_sleep_seconds: float = 5
    model_config = SettingsConfigDict(env_file=".env", env_prefix="OTHERS_")


class Settings(BaseSettings):
    postgres: PostgresSettings = PostgresSettings()
    elastic: ElasticSettings = ElasticSettings()
    others: OthersSettings = OthersSettings()


settings = Settings()
