from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    groq_api_key: str
    mongodb_uri: str
    mongodb_db_name: str
    agent_working_directory: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()