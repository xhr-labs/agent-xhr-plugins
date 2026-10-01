from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    REQUEST_HEADERS: str = "{}"
    API_BASE_URL: str = ""

    model_config = SettingsConfigDict(env_file=".env")

