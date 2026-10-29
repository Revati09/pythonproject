import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from core import DEMO_PASSWORD, DataManager, SessionManager, SkillAnalytics, SkillMatcher


class SkillSwapCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.data = DataManager(Path(self.temporary_directory.name))
        self.students = self.data.load_students()
        self.sakshu = self.students[0]
        self.vaishnavi = self.students[1]

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_demo_login_and_password_validation(self) -> None:
        logged_in = self.data.authenticate("SAKSHU@example.com", DEMO_PASSWORD)
        self.assertEqual(logged_in.student_id, self.sakshu.student_id)
        with self.assertRaisesRegex(ValueError, "incorrect"):
            self.data.authenticate(self.sakshu.email, "incorrect-password")
        with self.assertRaisesRegex(ValueError, "8 characters"):
            self.data.register_student("New Student", "new@example.com", "short")

    def test_final_demo_roster_and_seed_sessions(self) -> None:
        self.assertEqual(
            [student.name for student in self.students],
            ["Sakshu", "Vaishnavi", "Anjali", "Revati"],
        )
        self.assertEqual(len(self.data.load_sessions()), 6)
        matches = SkillMatcher().find_reciprocal_matches(
            self.students[2],
            self.students,
        )
        self.assertEqual(
            [match.student.name for match in matches],
            ["Revati", "Sakshu"],
        )

    def test_registration_and_profile_skill_updates(self) -> None:
        student = self.data.register_student("New Student", "new@example.com", "password8")
        updated = self.data.update_profile(
            student.student_id,
            "New Student",
            "new@example.com",
            ["Rust", "Rust"],
            ["Python"],
        )
        self.assertEqual(updated.teaching_skills, ["Rust"])
        self.assertEqual(updated.learning_skills, ["Python"])
        self.assertEqual(self.data.authenticate("new@example.com", "password8"), updated)

    def test_reciprocal_matching_and_skill_search(self) -> None:
        matcher = SkillMatcher()
        matches = matcher.find_reciprocal_matches(self.sakshu, self.students)
        matches_by_id = {match.student.student_id: match for match in matches}
        self.assertEqual(set(matches_by_id), {"STU002", "STU003"})
        self.assertEqual(
            matches_by_id["STU002"].they_can_teach,
            ["Public Speaking", "Graphic Design"],
        )
        self.assertEqual(matches_by_id["STU002"].you_can_teach, ["Python", "Excel"])
        results = matcher.search_by_skill("graphic", self.students, "STU001")
        self.assertEqual([student.student_id for student in results], ["STU002"])
        with self.assertRaisesRegex(ValueError, "Enter a skill"):
            matcher.search_by_skill(" ", self.students)

    def test_session_status_feedback_and_rating(self) -> None:
        manager = SessionManager(self.data)
        session = manager.create_session(
            "STU002",
            "STU001",
            "Graphic Design",
            (date.today() + timedelta(days=1)).isoformat(),
        )
        with self.assertRaisesRegex(ValueError, "Completed"):
            manager.save_feedback(session.session_id, "Good lesson", 5)
        manager.update_status(session.session_id, "Completed")
        manager.save_feedback(session.session_id, "Very helpful", 5)
        saved = manager.get_session(session.session_id)
        self.assertEqual(saved.feedback, "Very helpful")
        self.assertEqual(saved.rating, 5)
        with self.assertRaisesRegex(ValueError, "YYYY-MM-DD"):
            manager.create_session("STU002", "STU001", "Graphic Design", "tomorrow")
        with self.assertRaisesRegex(ValueError, "whole number"):
            manager.save_feedback(session.session_id, "Bad rating", 6)

    def test_pandas_numpy_analytics(self) -> None:
        analytics = SkillAnalytics()
        popular = analytics.popular_skills(self.students)
        self.assertEqual(popular["python"], 1)
        completed, total, average = analytics.summary(self.data.load_sessions())
        self.assertEqual((completed, total), (2, 6))
        self.assertEqual(average, 4.5)


if __name__ == "__main__":
    unittest.main()
