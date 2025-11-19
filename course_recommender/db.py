# course_recommender/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .settings import settings

# Use the DATABASE_URL setting (uppercase, matching Settings class)
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# For SQLite we need check_same_thread=False, but not for Postgres
connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    future=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)
