from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_DATABASE_URI : str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")