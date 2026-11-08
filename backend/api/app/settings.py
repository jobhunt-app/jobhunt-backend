from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    app_name: str = "jobhunt-api"
    log_level: str = "INFO"
    version: str = "0.0.1"
    database_url: str = "postgresql+asyncpg://postgres:dev@localhost:5432/jobhunt"
