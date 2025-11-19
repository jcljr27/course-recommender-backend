# course_recommender/api/__init__.py

"""
API routers for the Course Recommendation Engine.
"""

from .courses import router as courses_router  # noqa: F401
from .recommendations import router as recommendations_router  # noqa: F401

__all__ = ["courses_router", "recommendations_router"]
