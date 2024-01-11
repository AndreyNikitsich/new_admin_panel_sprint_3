import logging.config
import os
from functools import cached_property
from typing import Dict

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR_PATH = os.path.dirname(os.path.abspath(__file__))


class PostgresSettings(BaseSettings):
    dbname: str = "movies_admin"
    user: str = "movies_admin"
    host: str = "postgres"
    port: int = 5432
    password: str = "movies_admin"
    options: str = "-c search_path=content"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="POSTGRES_")


class ElasticSettings(BaseSettings):
    host: str = "elastic"
    port: int = 9200
    connection_schema: str = "http"
    index_name: str = "movies"
    index_file_name: str = "index_config.json"

    @cached_property
    def url(self):
        return f"{self.connection_schema}://{self.host}:{self.port}"

    @cached_property
    def index_file_path(self):
        return BASE_DIR_PATH / self.index_file_name

    model_config = SettingsConfigDict(env_file=".env", env_prefix="ELASTIC_")

class RedisSettings(BaseSettings):
    host: str = "redis"
    port: int = 6379

    model_config = SettingsConfigDict(env_file=".env", env_prefix="REDIS_")


class OthersSettings(BaseSettings):
    etl_sleep_seconds: float = 5
    elastic_backoff_max_time: float = 60 * 5
    postgres_backoff_max_time: float = 60 * 5
    logging_level: str = "INFO"
    model_config = SettingsConfigDict(env_file=".env", env_prefix="OTHERS_")


class Settings(BaseSettings):
    postgres: PostgresSettings = PostgresSettings()
    elastic: ElasticSettings = ElasticSettings()
    redis: RedisSettings = RedisSettings()
    others: OthersSettings = OthersSettings()


settings = Settings()

LOGGING_CONFIG: Dict = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "default": {"format": "[%(levelname)s] %(asctime)s  %(process)s %(name)s.%(funcName)s: %(message)s"}
    },
    "handlers": {
        "stdout": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "default",
        },
        "stderr": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
            "formatter": "default",
        },
    },
    "loggers": {
        "__main__": {
            "handlers": ["stdout"],
            "level": settings.others.logging_level,
        },
        "etl": {
            "handlers": ["stdout"],
            "level": settings.others.logging_level,
        },
        "elastic_init": {
            "handlers": ["stdout"],
            "level": settings.others.logging_level,
        },
        "backoff": {
            "handlers": ["stderr"],
            "level": "INFO",
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
