import numpy as np
import pytest
from scipy import sparse

from course_recommender.recommender import (
    build_student_profile_vector,
    recommend_courses,
)


@pytest.fixture
def sample_courses():
    # Three simple courses for testing
    return [
        {
            "course_id": "CS101",
            "course_name": "Intro to CS",
            "description": "intro programming basics",
            "tags": ["cs", "intro"],
            "difficulty": 1,
            "workload": 2,
            "type": "major",
            "prerequisites": []
        },
        {
            "course_id": "CS102",
            "course_name": "Data Structures",
            "description": "data structures and algorithms",
            "tags": ["cs", "data"],
            "difficulty": 3,
            "workload": 3,
            "type": "major",
            "prerequisites": ["CS101"]
        },
        {
            "course_id": "CS201",
            "course_name": "Algorithms",
            "description": "advanced algorithms and complexity",
            "tags": ["cs", "algorithms"],
            "difficulty": 4,
            "workload": 4,
            "type": "major",
            "prerequisites": ["CS102"]
        },
    ]


@pytest.fixture
def fake_vectorizer():
    """
    Fake vectorizer that returns simple numeric vectors.
    This only needs a transform_text method to mimic CourseVectorizer.
    """
    class FakeVectorizer:
        def transform_text(self, texts):
            # Return deterministic vectors based on text length
            arr = np.array([[len(texts[0]) % 5, len(texts[0]) % 7]], dtype=float)
            return sparse.csr_matrix(arr)

    return FakeVectorizer()


@pytest.fixture
def course_matrix():
    """
    A simple fake course matrix (3 courses x 2 features).
    """
    data = np.array([
        [1.0, 0.5],   # CS101
        [0.8, 0.9],   # CS102
        [0.3, 1.2],   # CS201
    ])
    return sparse.csr_matrix(data)


@pytest.fixture
def id_to_index():
    return {
        "CS101": 0,
        "CS102": 1,
        "CS201": 2,
    }


# -----------------------------------------------------------
# 1. Test recommender runs without error
# -----------------------------------------------------------
def test_recommender_runs(sample_courses, course_matrix, id_to_index, fake_vectorizer):
    completed = ["CS101"]
    interests = ["cs", "algorithms"]

    student_vec = build_student_profile_vector(
        course_matrix=course_matrix,
        id_to_index=id_to_index,
        completed_course_ids=completed,
        interest_tags=interests,
        vectorizer=fake_vectorizer,
    )

    recs = recommend_courses(
        course_matrix=course_matrix,
        student_vec=student_vec,
        courses=sample_courses,
        id_to_index=id_to_index,
        completed_course_ids=completed,
        allow_future_courses=True,
        top_k=5,
    )

    assert isinstance(recs, list)
    assert len(recs) > 0  # Should recommend at least something


# -----------------------------------------------------------
# 2. Recommended courses should NOT include completed courses
# -----------------------------------------------------------
def test_excludes_completed_courses(sample_courses, course_matrix, id_to_index, fake_vectorizer):
    completed = ["CS101"]
    interests = ["cs"]

    student_vec = build_student_profile_vector(
        course_matrix=course_matrix,
        id_to_index=id_to_index,
        completed_course_ids=completed,
        interest_tags=interests,
        vectorizer=fake_vectorizer,
    )

    recs = recommend_courses(
        course_matrix=course_matrix,
        student_vec=student_vec,
        courses=sample_courses,
        id_to_index=id_to_index,
        completed_course_ids=completed,
        allow_future_courses=True,
        top_k=5,
    )

    returned_ids = [r["course_id"] for r in recs]
    assert "CS101" not in returned_ids


# -----------------------------------------------------------
# 3. When allow_future_courses=False, courses with missing prereqs 
#    must NOT appear
# -----------------------------------------------------------
def test_prereq_filtering(sample_courses, course_matrix, id_to_index, fake_vectorizer):
    completed = []   # student completed no courses
    interests = ["cs"]

    student_vec = build_student_profile_vector(
        course_matrix=course_matrix,
        id_to_index=id_to_index,
        completed_course_ids=completed,
        interest_tags=interests,
        vectorizer=fake_vectorizer,
    )

    recs = recommend_courses(
        course_matrix=course_matrix,
        student_vec=student_vec,
        courses=sample_courses,
        id_to_index=id_to_index,
        completed_course_ids=completed,
        allow_future_courses=False,  # strict prereq enforcement
        top_k=5,
    )

    returned_ids = [r["course_id"] for r in recs]

    # CS102 requires CS101 → should NOT appear
    assert "CS102" not in returned_ids

    # CS201 requires CS102 → should NOT appear
    assert "CS201" not in returned_ids

    # Only CS101 has no prereqs
    assert returned_ids == ["CS101"]
