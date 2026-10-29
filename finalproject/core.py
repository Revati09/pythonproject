import hashlib
import hmac
import json
import os
import re
import secrets
import tempfile
import uuid
from collections.abc import Iterable
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from models import ExchangeSession, Student


DEMO_PASSWORD = "skill123"
PASSWORD_ITERATIONS = 200_000
SESSION_STATUSES = {"Planned", "Completed", "Cancelled"}


def _password_hash(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        PASSWORD_ITERATIONS,
    ).hex()


def _new_student(
    student_id: str,
    name: str,
    email: str,
    teaching_skills: list[str],
    learning_skills: list[str],
    password: str,
) -> Student:
    salt = secrets.token_hex(16)
    return Student(
        student_id=student_id,
        name=name,
        email=email.strip().casefold(),
        teaching_skills=teaching_skills,
        learning_skills=learning_skills,
        password_salt=salt,
        password_hash=_password_hash(password, salt),
    )


class DataManager:
    """Persists student profiles and exchange sessions as JSON files."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or Path(__file__).resolve().parent / "data"
        self.students_file = self.data_dir / "students.json"
        self.sessions_file = self.data_dir / "sessions.json"
        self._initialize_students()
        self._initialize_sessions()

    @staticmethod
    def _sample_students() -> list[Student]:
        return [
            _new_student(
                "STU001",
                "Sakshu",
                "sakshu@example.com",
                ["Python", "Excel"],
                ["Public Speaking", "Graphic Design", "Data Analysis"],
                DEMO_PASSWORD,
            ),
            _new_student(
                "STU002",
                "Vaishnavi",
                "vaishnavi@example.com",
                ["Public Speaking", "Graphic Design"],
                ["Python", "Excel"],
                DEMO_PASSWORD,
            ),
            _new_student(
                "STU003",
                "Anjali",
                "anjali@example.com",
                ["Java", "Data Analysis"],
                ["UI/UX Design", "Public Speaking", "Excel"],
                DEMO_PASSWORD,
            ),
            _new_student(
                "STU004",
                "Revati",
                "revati@example.com",
                ["UI/UX Design", "Public Speaking"],
                ["Java", "Data Analysis"],
                DEMO_PASSWORD,
            ),
        ]

    def _initialize_students(self) -> None:
        if not self.students_file.exists():
            self.save_students(self._sample_students())
            return
        data = self._read_json(self.students_file)
        if not isinstance(data, list):
            raise ValueError("students.json must contain a list of students.")
        migrated = False
        for record in data:
            if not isinstance(record, dict):
                raise ValueError("Each student record must be a JSON object.")
            if "password_salt" not in record and "password_hash" not in record:
                salt = secrets.token_hex(16)
                record["password_salt"] = salt
                record["password_hash"] = _password_hash(DEMO_PASSWORD, salt)
                migrated = True
        students = [Student.from_dict(record) for record in data]
        if migrated:
            self.save_students(students)

    def _initialize_sessions(self) -> None:
        if self.sessions_file.exists():
            self.load_sessions()
            return
        today = date.today()
        self.save_sessions(
            [
                ExchangeSession(
                    session_id="DEMO-001",
                    teacher_id="STU001",
                    learner_id="STU002",
                    skill="Python",
                    session_date=(today - timedelta(days=5)).isoformat(),
                    status="Completed",
                    feedback="Clear explanations and useful practice exercises.",
                    rating=5,
                ),
                ExchangeSession(
                    session_id="DEMO-002",
                    teacher_id="STU002",
                    learner_id="STU001",
                    skill="Graphic Design",
                    session_date=(today - timedelta(days=4)).isoformat(),
                    status="Completed",
                    feedback="Learned the basics of layout and color.",
                    rating=4,
                ),
                ExchangeSession(
                    session_id="DEMO-003",
                    teacher_id="STU003",
                    learner_id="STU001",
                    skill="Data Analysis",
                    session_date=(today + timedelta(days=1)).isoformat(),
                ),
                ExchangeSession(
                    session_id="DEMO-004",
                    teacher_id="STU001",
                    learner_id="STU003",
                    skill="Excel",
                    session_date=(today + timedelta(days=2)).isoformat(),
                ),
                ExchangeSession(
                    session_id="DEMO-005",
                    teacher_id="STU003",
                    learner_id="STU004",
                    skill="Java",
                    session_date=(today + timedelta(days=3)).isoformat(),
                ),
                ExchangeSession(
                    session_id="DEMO-006",
                    teacher_id="STU004",
                    learner_id="STU003",
                    skill="UI/UX Design",
                    session_date=(today + timedelta(days=4)).isoformat(),
                ),
            ]
        )

    @staticmethod
    def _read_json(path: Path) -> object:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError(
                f"{path.name} has invalid JSON at line {error.lineno}: {error.msg}"
            ) from error

    @staticmethod
    def _write_json(path: Path, records: list[dict[str, object]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=path.parent,
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                json.dump(records, temporary_file, indent=2, ensure_ascii=False)
                temporary_file.write("\n")
            os.replace(temporary_path, path)
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()

    @staticmethod
    def validate_profile(name: str, email: str, password: str | None = None) -> None:
        if not name.strip():
            raise ValueError("Name cannot be empty.")
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()):
            raise ValueError("Enter a valid email address.")
        if password is not None and len(password) < 8:
            raise ValueError("Password must contain at least 8 characters.")

    @staticmethod
    def _validate_skills(skills: Iterable[str]) -> list[str]:
        result: list[str] = []
        seen: set[str] = set()
        for item in skills:
            skill = item.strip()
            normalized = skill.casefold()
            if skill and normalized not in seen:
                result.append(skill)
                seen.add(normalized)
        return result

    def load_students(self) -> list[Student]:
        data = self._read_json(self.students_file)
        if not isinstance(data, list):
            raise ValueError("students.json must contain a list of students.")
        return [Student.from_dict(record) for record in data]

    def save_students(self, students: list[Student]) -> None:
        self._write_json(
            self.students_file,
            [student.to_dict() for student in students],
        )

    def load_sessions(self) -> list[ExchangeSession]:
        data = self._read_json(self.sessions_file)
        if not isinstance(data, list):
            raise ValueError("sessions.json must contain a list of sessions.")
        return [ExchangeSession.from_dict(record) for record in data]

    def save_sessions(self, sessions: list[ExchangeSession]) -> None:
        self._write_json(
            self.sessions_file,
            [session.to_dict() for session in sessions],
        )

    def register_student(self, name: str, email: str, password: str) -> Student:
        self.validate_profile(name, email, password)
        students = self.load_students()
        normalized_email = email.strip().casefold()
        if any(student.email.casefold() == normalized_email for student in students):
            raise ValueError("An account with this email already exists.")
        student = _new_student(
            uuid.uuid4().hex[:8].upper(),
            name.strip(),
            normalized_email,
            [],
            [],
            password,
        )
        students.append(student)
        self.save_students(students)
        return student

    def authenticate(self, email: str, password: str) -> Student:
        normalized_email = email.strip().casefold()
        for student in self.load_students():
            if student.email.casefold() != normalized_email:
                continue
            actual_hash = _password_hash(password, student.password_salt)
            if hmac.compare_digest(actual_hash, student.password_hash):
                return student
            break
        raise ValueError("Email or password is incorrect.")

    def get_student(self, student_id: str) -> Student:
        for student in self.load_students():
            if student.student_id == student_id:
                return student
        raise ValueError("The selected student no longer exists.")

    def update_profile(
        self,
        student_id: str,
        name: str,
        email: str,
        teaching_skills: list[str],
        learning_skills: list[str],
    ) -> Student:
        self.validate_profile(name, email)
        students = self.load_students()
        normalized_email = email.strip().casefold()
        if any(
            student.student_id != student_id
            and student.email.casefold() == normalized_email
            for student in students
        ):
            raise ValueError("Another student already uses this email.")
        for index, student in enumerate(students):
            if student.student_id == student_id:
                updated = Student(
                    student_id=student.student_id,
                    name=name.strip(),
                    email=normalized_email,
                    teaching_skills=self._validate_skills(teaching_skills),
                    learning_skills=self._validate_skills(learning_skills),
                    password_salt=student.password_salt,
                    password_hash=student.password_hash,
                )
                students[index] = updated
                self.save_students(students)
                return updated
        raise ValueError("The student profile no longer exists.")


class ReciprocalMatch:
    """Two-way skill exchange details for a potential partner."""

    def __init__(
        self,
        student: Student,
        they_can_teach: list[str],
        you_can_teach: list[str],
    ) -> None:
        self.student = student
        self.they_can_teach = they_can_teach
        self.you_can_teach = you_can_teach


class SkillMatcher:
    """Finds students with two-way teaching and learning skill overlap."""

    @staticmethod
    def _overlap(wanted: list[str], offered: list[str]) -> list[str]:
        offered_by_normalized = {skill.casefold(): skill for skill in offered}
        return [
            offered_by_normalized[skill.casefold()]
            for skill in wanted
            if skill.casefold() in offered_by_normalized
        ]

    def find_reciprocal_matches(
        self,
        student: Student,
        students: list[Student],
    ) -> list[ReciprocalMatch]:
        matches: list[ReciprocalMatch] = []
        for other in students:
            if other.student_id == student.student_id:
                continue
            they_can_teach = self._overlap(
                student.learning_skills,
                other.teaching_skills,
            )
            you_can_teach = self._overlap(
                other.learning_skills,
                student.teaching_skills,
            )
            if they_can_teach and you_can_teach:
                matches.append(
                    ReciprocalMatch(other, they_can_teach, you_can_teach)
                )
        return sorted(matches, key=lambda match: match.student.name.casefold())

    @staticmethod
    def search_by_skill(
        skill: str,
        students: list[Student],
        exclude_student_id: str | None = None,
    ) -> list[Student]:
        query = skill.strip().casefold()
        if not query:
            raise ValueError("Enter a skill to search for.")
        return [
            student
            for student in students
            if student.student_id != exclude_student_id
            and any(query in offered.casefold() for offered in student.teaching_skills)
        ]


class SessionManager:
    """Creates sessions and tracks status, feedback, and ratings."""

    def __init__(self, data_manager: DataManager) -> None:
        self.data_manager = data_manager

    def create_session(
        self,
        teacher_id: str,
        learner_id: str,
        skill: str,
        session_date: str,
    ) -> ExchangeSession:
        if teacher_id == learner_id:
            raise ValueError("A student cannot schedule a session with themselves.")
        if not skill.strip():
            raise ValueError("Enter the skill for this session.")
        try:
            parsed_date = date.fromisoformat(session_date.strip())
        except ValueError as error:
            raise ValueError("Enter the session date as YYYY-MM-DD.") from error
        if parsed_date < date.today():
            raise ValueError("Choose today or a future date for a new session.")
        students = {student.student_id: student for student in self.data_manager.load_students()}
        teacher = students.get(teacher_id)
        learner = students.get(learner_id)
        if teacher is None or learner is None:
            raise ValueError("Both students must have valid profiles.")
        if not any(
            offered.casefold() == skill.strip().casefold()
            for offered in teacher.teaching_skills
        ):
            raise ValueError("The selected student does not list this teaching skill.")
        session = ExchangeSession(
            session_id=uuid.uuid4().hex[:10].upper(),
            teacher_id=teacher_id,
            learner_id=learner_id,
            skill=skill.strip(),
            session_date=parsed_date.isoformat(),
        )
        sessions = self.data_manager.load_sessions()
        sessions.append(session)
        self.data_manager.save_sessions(sessions)
        return session

    def list_for_student(self, student_id: str) -> list[ExchangeSession]:
        return sorted(
            (
                session
                for session in self.data_manager.load_sessions()
                if student_id in {session.teacher_id, session.learner_id}
            ),
            key=lambda session: (session.session_date, session.session_id),
        )

    def get_session(self, session_id: str) -> ExchangeSession:
        for session in self.data_manager.load_sessions():
            if session.session_id == session_id:
                return session
        raise ValueError("The selected session no longer exists.")

    def update_status(self, session_id: str, status: str) -> ExchangeSession:
        if status not in SESSION_STATUSES:
            raise ValueError("Choose Planned, Completed, or Cancelled.")
        sessions = self.data_manager.load_sessions()
        for index, session in enumerate(sessions):
            if session.session_id == session_id:
                sessions[index].status = status
                self.data_manager.save_sessions(sessions)
                return sessions[index]
        raise ValueError("The selected session no longer exists.")

    def save_feedback(
        self,
        session_id: str,
        feedback: str,
        rating: int,
    ) -> ExchangeSession:
        if not isinstance(rating, int) or isinstance(rating, bool) or not 1 <= rating <= 5:
            raise ValueError("Rating must be a whole number from 1 to 5.")
        if len(feedback.strip()) > 500:
            raise ValueError("Feedback must be 500 characters or fewer.")
        sessions = self.data_manager.load_sessions()
        for index, session in enumerate(sessions):
            if session.session_id == session_id:
                if session.status != "Completed":
                    raise ValueError("Mark the session Completed before giving feedback.")
                sessions[index].feedback = feedback.strip()
                sessions[index].rating = rating
                self.data_manager.save_sessions(sessions)
                return sessions[index]
        raise ValueError("The selected session no longer exists.")


class SkillAnalytics:
    """Uses Pandas and NumPy to summarize students and sessions."""

    @staticmethod
    def popular_skills(students: list[Student]) -> pd.Series:
        rows = [
            {"student_id": student.student_id, "skill": skill.strip()}
            for student in students
            for skill in student.teaching_skills
            if skill.strip()
        ]
        frame = pd.DataFrame(rows, columns=["student_id", "skill"])
        if frame.empty:
            return pd.Series(dtype="int64")
        frame["skill_key"] = frame["skill"].str.casefold()
        return (
            frame.groupby("skill_key")["student_id"]
            .nunique()
            .sort_values(ascending=False)
        )

    @staticmethod
    def summary(sessions: list[ExchangeSession]) -> tuple[int, int, float]:
        completed = [session for session in sessions if session.status == "Completed"]
        ratings = np.array(
            [session.rating for session in completed if session.rating is not None],
            dtype=float,
        )
        average_rating = float(np.mean(ratings)) if ratings.size else 0.0
        return len(completed), len(sessions), average_rating
