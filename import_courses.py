# import_courses.py
import json
from pathlib import Path

from course_recommender.db import engine, SessionLocal
from course_recommender.models import Base, Course, CourseTag, CoursePrerequisite
from course_recommender.settings import settings


def main():
    # Just so you can see which DB this is hitting
    print(f"Using database: {engine.url}")

    # 1. DROP all tables and recreate them to match current models
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)

    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)

    # 2. Resolve courses.json path from settings.COURSES_PATH
    courses_path = Path(settings.COURSES_PATH)
    if not courses_path.exists():
        raise FileNotFoundError(f"courses.json not found at {courses_path}")

    print(f"Loading courses from: {courses_path}")
    with courses_path.open("r", encoding="utf-8") as f:
        courses_data = json.load(f)

    session = SessionLocal()
    try:
        for course in courses_data:
            c = Course(
                course_id=course["course_id"],
                course_name=course["course_name"],
                description=course.get("description", ""),
                credits=course.get("credits", 0),
                difficulty=course.get("difficulty", 3),
                workload=course.get("workload", 3),
                type=course.get("type", "elective"),
            )
            session.add(c)
            session.flush()  # so c.id is populated

            # --- TAGS: dedupe per course to avoid UNIQUE constraint errors ---
            raw_tags = course.get("tags", []) or []
            # preserve order while removing duplicates
            seen = set()
            deduped_tags = []
            for t in raw_tags:
                if t not in seen:
                    seen.add(t)
                    deduped_tags.append(t)

            for tag in deduped_tags:
                session.add(CourseTag(course_id=c.id, tag=tag))

            # --- PREREQS: also dedupe just in case ---
            raw_prereqs = course.get("prerequisites", []) or []
            seen_pr = set()
            deduped_prereqs = []
            for p in raw_prereqs:
                if p not in seen_pr:
                    seen_pr.add(p)
                    deduped_prereqs.append(p)

            for prereq in deduped_prereqs:
                session.add(
                    CoursePrerequisite(
                        course_id=c.id,
                        prereq_course_id=prereq,
                    )
                )

        session.commit()
        print(f"Imported {len(courses_data)} courses from {courses_path}")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
