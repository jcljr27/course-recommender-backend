# course_recommender/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database URL: SQLite locally, Postgres in production (via env var)
    database_url: str = "sqlite:///./courses.db"

    # Path to courses.json (used by import_courses.py)
    courses_path: str = "./courses.json"

    # Environment: "dev" or "prod"
    env: str = "dev"

    # Logging level for main.py
    log_level: str = "INFO"

    # TF-IDF / feature settings for the recommender
    tfidf_max_features: int = 500
    tfidf_ngram_min: int = 1
    tfidf_ngram_max: int = 2

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
