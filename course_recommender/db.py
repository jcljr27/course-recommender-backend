# course_recommender/db.py
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import sessionmaker

from .settings import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Decide connect_args based on driver (sqlite vs postgres, etc.)
url = make_url(SQLALCHEMY_DATABASE_URL)
connect_args = {}
if url.drivername.startswith("sqlite"):
    # Needed for SQLite in some contexts (e.g., FastAPI with threads)
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
