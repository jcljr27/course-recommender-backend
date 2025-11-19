# course_recommender/recommender.py
from __future__ import annotations

from typing import Dict, List, Optional
import numpy as np
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity


def build_student_profile_vector(
    *,
    course_matrix,
    id_to_index: Dict[str, int],
    completed_course_ids: List[str],
    interest_tags: List[str],
    vectorizer,
):
    """
    Build a 1 x n_features student profile vector.

    - If completed courses are provided, average their course vectors.
    - If interest tags are provided, build a TF-IDF vector from them.
    - If both are provided, average the two components.
    - If neither is provided, raise ValueError (handled by API layer).

    Returns: np.ndarray with shape (1, n_features)
    """
    components: List[np.ndarray] = []

    # ---- Component 1: completed courses ----
    valid_completed_indices: List[int] = []
    for cid in completed_course_ids:
        idx = id_to_index.get(cid)
        if idx is not None:
            valid_completed_indices.append(idx)

    if valid_completed_indices:
        completed_vecs = course_matrix[valid_completed_indices]  # shape (k, n_features)
        completed_mean = completed_vecs.mean(axis=0)

        # Convert to ndarray and ensure shape (1, n_features)
        completed_mean = np.asarray(completed_mean)
        if completed_mean.ndim == 1:
            completed_mean = completed_mean.reshape(1, -1)
        components.append(completed_mean)

    # ---- Component 2: interest tags ----
    if interest_tags:
        tags_text = " ".join(interest_tags)

        # Our project wraps TfidfVectorizer inside CourseVectorizer,
        # which exposes .transform_text(). Fall back to .transform()
        # if a raw TfidfVectorizer is passed instead.
        if hasattr(vectorizer, "transform_text"):
            tags_vec = vectorizer.transform_text([tags_text])
        else:
            tags_vec = vectorizer.transform([tags_text])

        # tags_vec is usually a sparse matrix; convert to ndarray.
        if sparse.issparse(tags_vec):
            tags_arr = tags_vec.toarray()
        else:
            tags_arr = np.asarray(tags_vec)

        if tags_arr.ndim == 1:
            tags_arr = tags_arr.reshape(1, -1)

        components.append(tags_arr)

    if not components:
        # This message is used in logs / HTTP 400 responses
        raise ValueError("Cannot build student profile: no completed courses or interest tags.")

    # Average all components to get final profile
    stacked = np.vstack(components)  # (num_components, n_features)
    profile = stacked.mean(axis=0, keepdims=True)  # (1, n_features)

    return profile  # np.ndarray, NOT np.matrix


def _get_missing_prereqs(course: dict, completed_course_ids: List[str]) -> List[str]:
    """
    Compute which prerequisites for a given course are not yet completed.
    """
    prereqs = course.get("prerequisites", []) or []
    completed_set = set(completed_course_ids)
    return [p for p in prereqs if p not in completed_set]


def _difficulty_weight(difficulty: int, preferred: Optional[str]) -> float:
    """
    Simple weighting function to nudge scores based on preferred difficulty.
    """
    if not preferred:
        return 1.0

    if preferred == "easy":
        return 1.1 if difficulty <= 2 else 0.9
    if preferred == "medium":
        return 1.1 if 2 <= difficulty <= 4 else 0.9
    if preferred == "hard":
        return 1.1 if difficulty >= 4 else 0.9

    return 1.0


def recommend_courses(
    *,
    course_matrix,
    student_vec,
    courses: List[dict],
    id_to_index: Dict[str, int],
    completed_course_ids: List[str],
    top_k: int = 10,
    allow_future_courses: bool = False,
    preferred_difficulty: Optional[str] = None,
) -> List[dict]:
    """
    Rank courses for a student using cosine similarity between the student
    profile vector and all course vectors.

    Returns a list of dicts:
    {
        "course_id": str,
        "course_name": str,
        "difficulty": int,
        "type": str,
        "score": float,
        "missing_prereqs": List[str],
    }
    """

    # ------------------------------------------------------------------
    # Ensure student_vec is compatible with scikit-learn
    # ------------------------------------------------------------------
    if isinstance(student_vec, np.matrix):
        student_vec = np.asarray(student_vec)

    if isinstance(student_vec, np.ndarray) and student_vec.ndim == 1:
        student_vec = student_vec.reshape(1, -1)

    # cosine_similarity supports sparse course_matrix + dense student_vec
    sims = cosine_similarity(student_vec, course_matrix)[0]  # (n_courses,)

    completed_set = set(completed_course_ids)
    candidates: List[dict] = []

    for idx, course in enumerate(courses):
        cid = course["course_id"]

        # Skip already completed courses
        if cid in completed_set:
            continue

        missing_prereqs = _get_missing_prereqs(course, completed_course_ids)

        # If future courses are not allowed, skip those with missing prereqs
        if not allow_future_courses and missing_prereqs:
            continue

        base_score = float(sims[idx])
        weight = _difficulty_weight(course.get("difficulty", 3), preferred_difficulty)
        final_score = base_score * weight

        candidates.append(
            {
                "course_id": cid,
                "course_name": course["course_name"],
                "difficulty": course["difficulty"],
                "type": course["type"],
                "score": final_score,
                "missing_prereqs": missing_prereqs,
            }
        )

    # Sort by score descending and limit to top_k
    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:top_k]
