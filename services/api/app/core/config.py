from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RESUME_APP_", env_file=".env")

    app_name: str = "Resume Generation API"
    app_version: str = "0.1.0"
    environment: str = Field(default="local")
    enable_docs: bool = True
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    max_resume_chars: int = 80_000
    max_jd_chars: int = 40_000


settings = Settings()

