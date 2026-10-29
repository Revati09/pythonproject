from dataclasses import asdict, dataclass
from datetime import date
from typing import Any


@dataclass
class Student:
    """Profile and login credentials for one student."""

    student_id: str
    name: str
    email: str
    teaching_skills: list[str]
    learning_skills: list[str]
    password_salt: str
    password_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: object) -> "Student":
        if not isinstance(data, dict):
            raise ValueError("Each student record must be a JSON object.")
        for field in ("student_id", "name", "email", "password_salt", "password_hash"):
            value = data.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Student field '{field}' must be a non-empty string.")
        for field in ("teaching_skills", "learning_skills"):
            skills = data.get(field)
            if not isinstance(skills, list) or not all(
                isinstance(skill, str) and skill.strip() for skill in skills
            ):
                raise ValueError(f"'{field}' must be a list of non-empty strings.")
        return cls(
            student_id=data["student_id"],
            name=data["name"],
            email=data["email"],
            teaching_skills=data["teaching_skills"],
            learning_skills=data["learning_skills"],
            password_salt=data["password_salt"],
            password_hash=data["password_hash"],
        )


@dataclass
class ExchangeSession:
    """A planned or completed one-way skill teaching session."""

    session_id: str
    teacher_id: str
    learner_id: str
    skill: str
    session_date: str
    status: str = "Planned"
    feedback: str = ""
    rating: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: object) -> "ExchangeSession":
        if not isinstance(data, dict):
            raise ValueError("Each session record must be a JSON object.")
        for field in (
            "session_id",
            "teacher_id",
            "learner_id",
            "skill",
            "session_date",
            "status",
            "feedback",
        ):
            value = data.get(field)
            if not isinstance(value, str):
                raise ValueError(f"Session field '{field}' must be text.")
        for field in ("session_id", "teacher_id", "learner_id", "skill"):
            if not data[field].strip():
                raise ValueError(f"Session field '{field}' cannot be empty.")
        if data["teacher_id"] == data["learner_id"]:
            raise ValueError("A student cannot be both teacher and learner.")
        if data["status"] not in {"Planned", "Completed", "Cancelled"}:
            raise ValueError("Session status must be Planned, Completed, or Cancelled.")
        try:
            date.fromisoformat(data["session_date"])
        except ValueError as error:
            raise ValueError("Session date must use YYYY-MM-DD format.") from error
        rating = data.get("rating")
        if rating is not None and (
            not isinstance(rating, int) or isinstance(rating, bool) or not 1 <= rating <= 5
        ):
            raise ValueError("Session rating must be an integer from 1 to 5.")
        if rating is not None and data["status"] != "Completed":
            raise ValueError("Only completed sessions can have a rating.")
        if len(data["feedback"]) > 500:
            raise ValueError("Session feedback must be 500 characters or fewer.")
        return cls(
            session_id=data["session_id"],
            teacher_id=data["teacher_id"],
            learner_id=data["learner_id"],
            skill=data["skill"],
            session_date=data["session_date"],
            status=data["status"],
            feedback=data["feedback"],
            rating=rating,
        )
