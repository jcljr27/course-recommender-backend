# course_recommender/models.py
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


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(String, unique=True, index=True, nullable=False)
    course_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    credits = Column(Integer, default=0)
    difficulty = Column(Integer, default=3)
    workload = Column(Integer, default=3)
    type = Column(String, default="elective")

    # relationships
    tags = relationship(
        "CourseTag",
        back_populates="course",
        cascade="all, delete-orphan",
    )
    prerequisites = relationship(
        "CoursePrerequisite",
        back_populates="course",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Course(course_id={self.course_id!r}, name={self.course_name!r})>"


class CourseTag(Base):
    __tablename__ = "course_tags"

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    tag = Column(String, nullable=False)

    course = relationship("Course", back_populates="tags")

    __table_args__ = (
        UniqueConstraint("course_id", "tag", name="uq_course_tag"),
    )

    def __repr__(self) -> str:
        return f"<CourseTag(course_id={self.course_id}, tag={self.tag!r})>"


class CoursePrerequisite(Base):
    __tablename__ = "course_prerequisites"

    id = Column(Integer, primary_key=True)
    # The course that has the prerequisite
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    # The prerequisite course, referenced by its course_id string (e.g. "CS101")
    prereq_course_id = Column(String, nullable=False)

    course = relationship("Course", back_populates="prerequisites")

    def __repr__(self) -> str:
        return f"<CoursePrerequisite(course_id={self.course_id}, prereq_course_id={self.prereq_course_id!r})>"


# --- Student profile-related models (for future use) ---


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True)
    student_id = Column(String, unique=True, index=True, nullable=False)
    major = Column(String, nullable=True)
    preferred_difficulty_min = Column(Integer, nullable=True)
    preferred_difficulty_max = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)

    completed_courses = relationship(
        "StudentCompletedCourse",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    interest_tags = relationship(
        "StudentInterestTag",
        back_populates="student",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<StudentProfile(student_id={self.student_id!r}, major={self.major!r})>"


class StudentCompletedCourse(Base):
    __tablename__ = "student_completed_courses"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    course_id = Column(String, nullable=False)  # store course_id like "CS101"

    student = relationship("StudentProfile", back_populates="completed_courses")

    __table_args__ = (
        UniqueConstraint("student_id", "course_id", name="uq_student_course"),
    )

    def __repr__(self) -> str:
        return f"<StudentCompletedCourse(student_id={self.student_id}, course_id={self.course_id!r})>"


class StudentInterestTag(Base):
    __tablename__ = "student_interest_tags"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    tag = Column(String, nullable=False)

    student = relationship("StudentProfile", back_populates="interest_tags")

    __table_args__ = (
        UniqueConstraint("student_id", "tag", name="uq_student_tag"),
    )

    def __repr__(self) -> str:
        return f"<StudentInterestTag(student_id={self.student_id}, tag={self.tag!r})>"
