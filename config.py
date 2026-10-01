from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    app_name: str = "FitBuddy"
    app_env: str = "development"
    database_url: str = "sqlite:///./fitbuddy.db"

    gemini_api_key: str | None = Field(default=None)
    gemini_workout_model: str = "gemini-3.8-flash"
    gemini_tip_model: str = "gemini-3.8-flash"

    admin_username: str = "admin"
    admin_password: str = "change-me"
    session_secret: str = "change-this-secret-in-production"

    ai_timeout_seconds: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @field_validator("ai_timeout_seconds")
    @classmethod
    def validate_timeout(cls, value: int) -> int:
        if not 5 <= value <= 300:
            raise ValueError("AI timeout must be between 5 and 300 seconds.")
        return value

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
