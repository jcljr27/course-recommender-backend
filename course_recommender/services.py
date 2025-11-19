# course_recommender/services.py
from typing import Dict, List, Optional
import logging

from fastapi import Request

from .data_loading import build_course_corpus, build_id_index_map
from .features import CourseVectorizer
from .recommender import build_student_profile_vector, recommend_courses
from .db import SessionLocal
from .db_utils import get_all_courses_for_recommender

logger = logging.getLogger("course_recommender_api")


class RecommenderService:
    """
    Thin service:
      - load courses from DB (via db_utils)
      - build vectorizer & matrix
      - score recommendations
    """

    def __init__(self):
        # Use a DB session + db_utils helper so all course-loading logic
        # lives in one place.
        db = SessionLocal()
        try:
            self.courses = get_all_courses_for_recommender(db)
        finally:
            db.close()

        # Build text corpus & vectorizer
        self.corpus = build_course_corpus(self.courses)
        self.vectorizer = CourseVectorizer()
        self.course_matrix = self.vectorizer.fit_transform_courses(self.corpus)

        self.id_to_index: Dict[str, int] = build_id_index_map(self.courses)

        logger.info(
            "RecommenderService initialized with %d courses from DB",
            len(self.courses),
        )

    def list_courses(self) -> List[dict]:
        """
        Return all courses as dicts (same format as recommender expects).
        """
        return self.courses

    def get_course(self, course_id: str) -> dict:
        """
        Get a single course dict by its course_id (e.g., 'CS101').
        """
        for c in self.courses:
            if c["course_id"] == course_id:
                return c
        raise KeyError(course_id)

    def recommend(
        self,
        *,
        completed_courses: List[str],
        interest_tags: List[str],
        preferred_difficulty: Optional[str],
        allow_future_courses: bool,
        top_k: int,
    ) -> List[dict]:
        """
        Run the recommendation pipeline for a given student state.
        """
        # basic validation: unknown course_ids
        unknown = [cid for cid in completed_courses if cid not in self.id_to_index]
        if unknown:
            raise ValueError(f"Unknown completed course_ids: {unknown}")

        student_vec = build_student_profile_vector(
            course_matrix=self.course_matrix,
            id_to_index=self.id_to_index,
            completed_course_ids=completed_courses,
            interest_tags=interest_tags,
            vectorizer=self.vectorizer,
        )

        recs = recommend_courses(
            course_matrix=self.course_matrix,
            student_vec=student_vec,
            courses=self.courses,
            id_to_index=self.id_to_index,
            completed_course_ids=completed_courses,
            top_k=top_k,
            allow_future_courses=allow_future_courses,
            preferred_difficulty=preferred_difficulty,
        )

        return recs


def get_recommender(request: Request) -> RecommenderService:
    """
    FastAPI dependency: pull the singleton service from app.state.
    """
    return request.app.state.recommender  # type: ignore[attr-defined]
