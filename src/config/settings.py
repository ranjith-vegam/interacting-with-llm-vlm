from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
from src.models.llm_settings import (
    TextModelSettings, 
    ImageModelSettings
)


class CorsSettings(BaseModel):
    allow_origins: List[str]
    allow_credentials: bool
    allow_methods: List[str]
    allow_headers: List[str]


class ServerSettings(BaseModel):
    port: int
    log_level: str
    log_path: str
    workers: int
    limit_concurrency: int
    cors: CorsSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__")
    environment: str
    api_key: str
    server: ServerSettings
    text_model: TextModelSettings
    image_model: ImageModelSettings

_config_instance = None


def get_config():
    """
    Returns the singleton instance of the Settings class.
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Settings()  # type: ignore
    return _config_instance


if __name__ == "__main__":
    settings = get_config()
    print(settings.model_dump())