# course_recommender/api/courses.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..schemas import CourseOut
from ..db_utils import (
    get_db,
    get_all_courses_for_recommender,
    get_course_for_recommender,
)

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("/", response_model=List[CourseOut])
def list_courses(db: Session = Depends(get_db)):
    """
    List all courses (loaded directly from the database).
    """
    courses = get_all_courses_for_recommender(db)
    return courses


@router.get("/{course_id}", response_model=CourseOut)
def get_course(course_id: str, db: Session = Depends(get_db)):
    """
    Get details for a single course by course_id (e.g., "CS101").
    """
    course = get_course_for_recommender(db, course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return course
