# course_recommender/api/recommendations.py
from typing import List
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..services import RecommenderService, get_recommender
from ..schemas import RecommendationRequest, RecommendationItem
from ..db_utils import get_db, get_student_profile_data

logger = logging.getLogger("course_recommender_api")

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("/", response_model=List[RecommendationItem])
def get_recommendations(
    req: RecommendationRequest,
    rec: RecommenderService = Depends(get_recommender),
    db: Session = Depends(get_db),
):
    """
    Get course recommendations for a student.

    Behavior:
      - If student_id is provided AND completed_courses / interest_tags
        are not provided, load them from the student profile.
      - Otherwise, use the completed_courses and interest_tags given
        in the request body.
    """
    timestamp = datetime.utcnow().isoformat() + "Z"

    # Resolve completed_courses and interest_tags
    completed_courses = req.completed_courses
    interest_tags = req.interest_tags

    if req.student_id and not (completed_courses or interest_tags):
        profile = get_student_profile_data(db, req.student_id)
        if profile is None:
            raise HTTPException(status_code=404, detail="Student profile not found")

        completed_courses = profile["completed_courses"]
        # If request provided interest_tags, keep them; otherwise use profile's
        interest_tags = interest_tags or profile["interest_tags"]

    try:
        recs = rec.recommend(
            completed_courses=completed_courses,
            interest_tags=interest_tags,
            preferred_difficulty=req.preferred_difficulty,
            allow_future_courses=req.allow_future_courses,
            top_k=req.top_k,
        )
    except ValueError as e:
        logger.warning(
            "[%s] /recommendations error: %s (completed_courses=%d)",
            timestamp,
            str(e),
            len(completed_courses),
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(
            "[%s] /recommendations unexpected error: %s",
            timestamp,
            str(e),
        )
        raise HTTPException(status_code=500, detail="Internal server error")

    logger.info(
        "[%s] /recommendations completed_courses=%d interest_tags=%d returned=%d",
        timestamp,
        len(completed_courses),
        len(interest_tags),
        len(recs),
    )

    return recs

