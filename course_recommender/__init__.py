# course_recommender/__init__.py

"""
Core package for the Course Recommendation Engine.
"""

from . import data_loading, features, recommender, schemas, services, settings  # noqa: F401

__all__ = [
    "data_loading",
    "features",
    "recommender",
    "schemas",
    "services",
    "settings",
]
