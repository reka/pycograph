"""Configuration for Pycograph."""

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Settings class."""

    overwrite_existing_graph: bool = False
    determine_test_types: bool = False
    redis_host: str = "localhost"
    redis_port: int = 6379


settings = Settings()
