# course_recommender/features.py
from typing import List

from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer

from .settings import settings


class CourseVectorizer:
    """
    Wraps a TF-IDF vectorizer for course descriptions + tags.
    Uses settings.tfidf_max_features as a default cap.
    """

    def __init__(self, max_features: int | None = None):
        if max_features is None:
            max_features = settings.tfidf_max_features

        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=max_features,
        )

    def fit_transform_courses(self, corpus: List[str]) -> csr_matrix:
        """
        Fit the vectorizer on the course corpus and return
        the course feature matrix.

        Shape: (n_courses, n_features)
        """
        return self.vectorizer.fit_transform(corpus)

    def transform_text(self, texts: List[str]) -> csr_matrix:
        """
        Transform arbitrary text (e.g., student interests) into TF-IDF vectors.

        Shape: (n_texts, n_features)
        """
        return self.vectorizer.transform(texts)
