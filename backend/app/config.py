from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str
    mongodb_uri: str
    mongodb_db_name: str
    agent_working_directory: str

    class Config:

        env_file = ".env"


settings = Settings()