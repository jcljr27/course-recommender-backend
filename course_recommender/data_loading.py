# course_recommender/data_loading.py
import json
from typing import List, Dict, Any


Course = Dict[str, Any]


def load_courses(path: str) -> List[Course]:
    """
    Load courses from a JSON file (list of course dicts).
    """
    with open(path, "r", encoding="utf-8") as f:
        courses: List[Course] = json.load(f)
    return courses


def build_course_corpus(courses: List[Course]) -> List[str]:
    """
    Build a text corpus for each course by combining
    name, description, and tags into a single string.
    """
    corpus: List[str] = []
    for c in courses:
        name = c.get("course_name", "") or ""
        desc = c.get("description", "") or ""
        tags = c.get("tags", []) or []
        if isinstance(tags, list):
            tags_text = " ".join(str(t) for t in tags)
        else:
            tags_text = str(tags)
        text = f"{name} {desc} {tags_text}"
        corpus.append(text)
    return corpus


def build_id_index_map(courses: List[Course]) -> Dict[str, int]:
    """
    Map course_id -> row index in the feature matrix.
    """
    return {c["course_id"]: idx for idx, c in enumerate(courses)}
