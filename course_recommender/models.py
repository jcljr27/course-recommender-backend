# course_recommender/models.py
from __future__ import annotations

from typing import List

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# ---------- Course & related tables ---------- #


class Course(Base):
    __tablename__ = "courses"
    # Allow legacy type annotations (without Mapped[])
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True, index=True)
    # This corresponds to "course_id" in courses.json, e.g. "CS101"
    course_id = Column(String(50), unique=True, index=True, nullable=False)

    course_name = Column(String(255), nullable=False)
    credits = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(Integer, nullable=False)
    workload = Column(Integer, nullable=False)
    type = Column(String(50), nullable=False)  # "major", "elective", etc.

    # Relationships
    tags: List["CourseTag"] = relationship(
        "CourseTag",
        back_populates="course",
        cascade="all, delete-orphan",
    )

    prerequisites: List["CoursePrerequisite"] = relationship(
        "CoursePrerequisite",
        back_populates="course",
        cascade="all, delete-orphan",
        foreign_keys="CoursePrerequisite.course_id",
    )


class CourseTag(Base):
    __tablename__ = "course_tags"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)
    course_id = Column(
        Integer,
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )
    tag = Column(String(100), nullable=False)

    course: Course = relationship("Course", back_populates="tags")

    __table_args__ = (
        UniqueConstraint("course_id", "tag", name="uq_course_tag"),
    )


class CoursePrerequisite(Base):
    """
    Represents a directed edge: course -> prerequisite_course
    """
    __tablename__ = "course_prerequisites"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)
    course_id = Column(
        Integer,
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )
    prerequisite_course_id = Column(
        Integer,
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )

    course: Course = relationship(
        "Course",
        foreign_keys=[course_id],
        back_populates="prerequisites",
    )
    prerequisite_course: Course = relationship(
        "Course",
        foreign_keys=[prerequisite_course_id],
    )

    __table_args__ = (
        UniqueConstraint(
            "course_id",
            "prerequisite_course_id",
            name="uq_course_prereq",
        ),
    )


# ---------- Student profile & related tables ---------- #


class StudentProfile(Base):
    __tablename__ = "student_profiles"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)
    student_id = Column(String(64), unique=True, index=True, nullable=False)
    major = Column(String(100), nullable=False)
    preferred_difficulty = Column(
        String(20), nullable=True
    )  # "easy", "medium", "hard", etc.
    notes = Column(Text, nullable=True)

    completed_courses: List["StudentCompletedCourse"] = relationship(
        "StudentCompletedCourse",
        back_populates="student",
        cascade="all, delete-orphan",
    )

    interest_tags: List["StudentInterestTag"] = relationship(
        "StudentInterestTag",
        back_populates="student",
        cascade="all, delete-orphan",
    )


class StudentCompletedCourse(Base):
    __tablename__ = "student_completed_courses"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)
    student_profile_id = Column(
        Integer,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    course_id = Column(
        Integer,
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )

    student: StudentProfile = relationship(
        "StudentProfile",
        back_populates="completed_courses",
    )
    course: Course = relationship("Course")

    __table_args__ = (
        UniqueConstraint(
            "student_profile_id",
            "course_id",
            name="uq_student_course",
        ),
    )


class StudentInterestTag(Base):
    __tablename__ = "student_interest_tags"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)
    student_profile_id = Column(
        Integer,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    tag = Column(String(100), nullable=False)

    student: StudentProfile = relationship(
        "StudentProfile",
        back_populates="interest_tags",
    )

    __table_args__ = (
        UniqueConstraint(
            "student_profile_id",
            "tag",
            name="uq_student_interest_tag",
        ),
    )
