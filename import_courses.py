# import_courses.py
import json
from pathlib import Path

from course_recommender.db import engine, SessionLocal
from course_recommender.models import Base, Course, CourseTag, CoursePrerequisite
from course_recommender.settings import settings


def main():
    # 1. Create tables (no-op if they already exist)
    Base.metadata.create_all(bind=engine)

    # 2. Load courses.json
    courses_path = Path(settings.courses_path)
    if not courses_path.exists():
        raise FileNotFoundError(f"courses.json not found at {courses_path}")

    with courses_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    session = SessionLocal()
    try:
        # Optional: clear existing data for a clean import
        session.query(CoursePrerequisite).delete()
        session.query(CourseTag).delete()
        session.query(Course).delete()
        session.commit()

        # 3. First pass: insert Course rows
        course_map = {}  # map from course_id string -> Course ORM object

        for item in data:
            course = Course(
                course_id=item["course_id"],
                course_name=item["course_name"],
                credits=item["credits"],
                description=item["description"],
                difficulty=item["difficulty"],
                workload=item["workload"],
                type=item["type"],
            )
            session.add(course)
            course_map[item["course_id"]] = course

        session.flush()  # assign IDs without committing yet

        # 4. Second pass: insert tags (deduplicated per course)
        for item in data:
            course = course_map[item["course_id"]]
            raw_tags = item.get("tags", []) or []

            seen_tags = set()
            for tag in raw_tags:
                if tag in seen_tags:
                    # Skip duplicates for this course to avoid UNIQUE constraint error
                    continue
                seen_tags.add(tag)
                session.add(CourseTag(course=course, tag=tag))

        session.flush()

        # 5. Third pass: insert prerequisites (course -> prerequisite_course)
        for item in data:
            course = course_map[item["course_id"]]
            for prereq_code in item.get("prerequisites", []) or []:
                prereq_course = course_map.get(prereq_code)
                if not prereq_course:
                    # If the prereq isn't in this dataset, skip (or log if you want)
                    continue
                session.add(
                    CoursePrerequisite(
                        course=course,
                        prerequisite_course=prereq_course,
                    )
                )

        # 6. Commit all changes
        session.commit()
        print(f"Imported {len(course_map)} courses into the database.")

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
