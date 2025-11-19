# course_recommender/db_utils.py
from typing import List, Optional, Dict, Any, Generator

from sqlalchemy.orm import Session, joinedload

from .db import SessionLocal
from .models import (
    Course as CourseModel,
    CoursePrerequisite,
    StudentProfile,
    StudentCompletedCourse,
    StudentInterestTag,
)


# ---------- DB session dependency ---------- #


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- Helper: Course → dict for recommender ---------- #


def _course_orm_to_dict(course: CourseModel) -> Dict[str, Any]:
    """
    Convert a Course ORM object to the dict format expected by the recommender:
    {
      "course_id": ...,
      "course_name": ...,
      "credits": ...,
      "tags": [...],
      "prerequisites": [...],
      "description": ...,
      "difficulty": ...,
      "workload": ...,
      "type": ...
    }
    """
    tags = [t.tag for t in course.tags]
    prereq_codes = [
        cp.prerequisite_course.course_id
        for cp in course.prerequisites
        if cp.prerequisite_course is not None
    ]

    return {
        "course_id": course.course_id,
        "course_name": course.course_name,
        "credits": course.credits,
        "tags": tags,
        "prerequisites": prereq_codes,
        "description": course.description,
        "difficulty": course.difficulty,
        "workload": course.workload,
        "type": course.type,
    }


# ---------- Public helpers ---------- #


def get_all_courses_for_recommender(db: Session) -> List[Dict[str, Any]]:
    """
    Fetch all courses from the DB and return them as a list of dicts
    in the format expected by the recommender.
    """
    orm_courses = (
        db.query(CourseModel)
        .options(
            joinedload(CourseModel.tags),
            joinedload(CourseModel.prerequisites).joinedload(
                CoursePrerequisite.prerequisite_course
            ),
        )
        .all()
    )

    return [_course_orm_to_dict(c) for c in orm_courses]


def get_course_for_recommender(db: Session, course_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch a single course by its human-readable course_id (e.g., "CS101")
    and return it as a dict for the recommender.
    Returns None if not found.
    """
    orm_course = (
        db.query(CourseModel)
        .options(
            joinedload(CourseModel.tags),
            joinedload(CourseModel.prerequisites).joinedload(
                CoursePrerequisite.prerequisite_course
            ),
        )
        .filter(CourseModel.course_id == course_id)
        .one_or_none()
    )

    if orm_course is None:
        return None

    return _course_orm_to_dict(orm_course)


def get_student_profile_data(
    db: Session,
    student_id: str,
) -> Optional[Dict[str, Any]]:
    """
    Fetch a student profile by student_id and return:
      {
        "student_id": ...,
        "major": ...,
        "preferred_difficulty": ...,
        "completed_courses": [course_id, ...],
        "interest_tags": [tag, ...]
      }

    Returns None if the student profile does not exist.
    """
    profile = (
        db.query(StudentProfile)
        .options(
            joinedload(StudentProfile.completed_courses).joinedload(
                StudentCompletedCourse.course
            ),
            joinedload(StudentProfile.interest_tags),
        )
        .filter(StudentProfile.student_id == student_id)
        .one_or_none()
    )

    if profile is None:
        return None

    completed_courses: List[str] = [
        sc.course.course_id
        for sc in profile.completed_courses
        if sc.course is not None
    ]
    interest_tags: List[str] = [t.tag for t in profile.interest_tags]

    return {
        "student_id": profile.student_id,
        "major": profile.major,
        "preferred_difficulty": profile.preferred_difficulty,
        "completed_courses": completed_courses,
        "interest_tags": interest_tags,
    }
