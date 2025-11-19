# course_recommender/schemas.py
from typing import List, Optional
from pydantic import BaseModel


class CourseOut(BaseModel):
    course_id: str
    course_name: str
    credits: int
    tags: List[str]
    description: str
    difficulty: int
    workload: int
    type: str
    prerequisites: List[str]


class RecommendationRequest(BaseModel):
    # NEW: optional student_id so backend can fetch profile data
    student_id: Optional[str] = None

    completed_courses: List[str] = []
    interest_tags: List[str] = []
    preferred_difficulty: Optional[str] = None  # "easy" | "medium" | "hard"
    allow_future_courses: bool = False
    top_k: int = 5


class RecommendationItem(BaseModel):
    course_id: str
    course_name: str
    difficulty: int
    type: str
    score: float
    missing_prereqs: List[str]
