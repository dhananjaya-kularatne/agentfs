from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    groq_api_key: str
    groq_model: str = "openai/gpt-oss-120b"
    mongodb_uri: str
    mongodb_db_name: str
    agent_working_directory: str

    # Comma-separated list of browser origins allowed to call this API.
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Per-client cap on agent task / confirm calls within a rolling window.
    rate_limit_max_tasks: int = 20
    rate_limit_window_seconds: int = 60

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def allowed_origins_list(self) -> list[str]:
        # Parsed list form of the comma-separated ALLOWED_ORIGINS string.
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


settings = Settings()