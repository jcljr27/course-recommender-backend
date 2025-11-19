from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database URL: can be SQLite locally, Postgres in production
    DATABASE_URL: str = "sqlite:///./courses.db"

    # Path to courses.json (used when importing or if you still support JSON)
    COURSES_PATH: str = "./courses.json"

    # Environment: "dev" or "prod"
    ENV: str = "dev"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
