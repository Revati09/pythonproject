import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from core import DataManager, SkillAnalytics, SkillMatcher, SessionManager
from models import ExchangeSession, Student


class SkillSwapApp:
    """Tkinter desktop interface for the SkillSwap student exchange app."""

    BACKGROUND = "#f4f7fb"
    NAVY = "#183153"
    GREEN = "#2f855a"
    MUTED = "#65758b"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("SkillSwap - Student Skill Exchange")
        self.root.geometry("1100x760")
        self.root.minsize(850, 620)
        self.root.configure(bg=self.BACKGROUND)

        self.data_manager = DataManager()
        self.matcher = SkillMatcher()
        self.session_manager = SessionManager(self.data_manager)
        self.analytics = SkillAnalytics()
        self.current_student: Student | None = None
        self._configure_styles()
        self._show_authentication()

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("Page.TFrame", background=self.BACKGROUND)
        style.configure(
            "Title.TLabel",
            background=self.BACKGROUND,
            foreground=self.NAVY,
            font=("Segoe UI", 26, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background=self.BACKGROUND,
            foreground=self.MUTED,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Section.TLabel",
            background=self.BACKGROUND,
            foreground=self.NAVY,
            font=("Segoe UI", 14, "bold"),
        )
        style.configure("Treeview", rowheight=29, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))

    def _clear_window(self) -> None:
        for widget in self.root.winfo_children():
            widget.destroy()

    def _show_authentication(self) -> None:
        self._clear_window()
        page = ttk.Frame(self.root, style="Page.TFrame", padding=(48, 34))
        page.pack(fill="both", expand=True)
        ttk.Label(page, text="SkillSwap", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            page,
            text="Teach what you know. Learn what you love.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(4, 20))

        notebook = ttk.Notebook(page)
        notebook.pack(fill="both", expand=True)
        login_tab = ttk.Frame(notebook, padding=24)
        register_tab = ttk.Frame(notebook, padding=24)
        notebook.add(login_tab, text="Log in")
        notebook.add(register_tab, text="Create account")
        self._build_login_form(login_tab)
        self._build_registration_form(register_tab)
        ttk.Label(
            page,
            text=(
                "Demo accounts: sakshu@example.com, vaishnavi@example.com, "
                "anjali@gmail.com, revati@example.com  |  Other demo passwords: "
                "skill123 (Anjali's existing password is unchanged)"
            ),
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(16, 0))

    def _build_login_form(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(1, weight=1)
        ttk.Label(parent, text="Welcome back", style="Section.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 18)
        )
        ttk.Label(parent, text="Email").grid(row=1, column=0, sticky="w", pady=6)
        email = ttk.Entry(parent, width=42)
        email.grid(row=1, column=1, sticky="ew", padx=(14, 0), pady=6)
        ttk.Label(parent, text="Password").grid(row=2, column=0, sticky="w", pady=6)
        password = ttk.Entry(parent, show="*", width=42)
        password.grid(row=2, column=1, sticky="ew", padx=(14, 0), pady=6)
        ttk.Button(
            parent,
            text="Log in",
            style="Accent.TButton",
            command=lambda: self._login(email.get(), password.get()),
        ).grid(row=3, column=1, sticky="e", pady=(16, 0))
        password.bind(
            "<Return>",
            lambda _event: self._login(email.get(), password.get()),
        )

    def _build_registration_form(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(1, weight=1)
        ttk.Label(parent, text="Join SkillSwap", style="Section.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 18)
        )
        fields: dict[str, ttk.Entry] = {}
        for row, label in enumerate(("Full name", "Email", "Password"), start=1):
            ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=6)
            entry = ttk.Entry(
                parent,
                width=42,
                show="*" if label == "Password" else "",
            )
            entry.grid(row=row, column=1, sticky="ew", padx=(14, 0), pady=6)
            fields[label] = entry
        ttk.Label(
            parent,
            text="Use at least 8 characters for your password.",
            style="Subtitle.TLabel",
        ).grid(row=4, column=1, sticky="w", pady=(4, 0))
        ttk.Button(
            parent,
            text="Create account",
            style="Accent.TButton",
            command=lambda: self._register(
                fields["Full name"].get(),
                fields["Email"].get(),
                fields["Password"].get(),
            ),
        ).grid(row=5, column=1, sticky="e", pady=(16, 0))

    def _login(self, email: str, password: str) -> None:
        try:
            self.current_student = self.data_manager.authenticate(email, password)
        except (OSError, ValueError) as error:
            messagebox.showerror("Unable to log in", str(error), parent=self.root)
            return
        self._show_dashboard()

    def _register(self, name: str, email: str, password: str) -> None:
        try:
            self.current_student = self.data_manager.register_student(
                name,
                email,
                password,
            )
        except (OSError, ValueError) as error:
            messagebox.showerror("Unable to create account", str(error), parent=self.root)
            return
        messagebox.showinfo(
            "Account created",
            "Your account is ready. Add your skills in the Profile tab.",
            parent=self.root,
        )
        self._show_dashboard()

    def _show_dashboard(self) -> None:
        self._clear_window()
        header = ttk.Frame(self.root, style="Page.TFrame", padding=(28, 16))
        header.pack(fill="x")
        ttk.Label(header, text="SkillSwap", style="Title.TLabel").pack(side="left")
        student_name = self.current_student.name if self.current_student else ""
        ttk.Label(
            header,
            text=f"Signed in as {student_name}",
            style="Subtitle.TLabel",
        ).pack(side="left", padx=20)
        ttk.Button(header, text="Log out", command=self._logout).pack(side="right")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        self.profile_tab = ttk.Frame(self.notebook, padding=20)
        self.match_tab = ttk.Frame(self.notebook, padding=20)
        self.search_tab = ttk.Frame(self.notebook, padding=20)
        self.sessions_tab = ttk.Frame(self.notebook, padding=20)
        self.analytics_tab = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.profile_tab, text="My profile")
        self.notebook.add(self.match_tab, text="Skill matches")
        self.notebook.add(self.search_tab, text="Search students")
        self.notebook.add(self.sessions_tab, text="Sessions")
        self.notebook.add(self.analytics_tab, text="Analytics")

        self._build_profile_tab()
        self._build_match_tab()
        self._build_search_tab()
        self._build_sessions_tab()
        self._build_analytics_tab()
        self._refresh_sessions()

    def _logout(self) -> None:
        self.current_student = None
        self._show_authentication()

    def _build_profile_tab(self) -> None:
        student = self._student()
        tab = self.profile_tab
        tab.columnconfigure(1, weight=1)
        ttk.Label(tab, text="Your student profile", style="Section.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 18)
        )

        self.profile_entries: dict[str, ttk.Entry] = {}
        values = (
            ("Full name", student.name),
            ("Email", student.email),
            ("Skills you can teach (comma-separated)", ", ".join(student.teaching_skills)),
            ("Skills you want to learn (comma-separated)", ", ".join(student.learning_skills)),
        )
        for row, (label, value) in enumerate(values, start=1):
            ttk.Label(tab, text=label).grid(row=row, column=0, sticky="w", pady=9)
            entry = ttk.Entry(tab)
            entry.insert(0, value)
            entry.grid(row=row, column=1, sticky="ew", padx=(18, 0), pady=9)
            self.profile_entries[label] = entry
        ttk.Label(
            tab,
            text="Add a skill by typing it, update it by editing it, or remove it "
            "by deleting it from the list.",
            style="Subtitle.TLabel",
            wraplength=680,
        ).grid(row=5, column=1, sticky="w", pady=(2, 12))
        ttk.Button(
            tab,
            text="Save profile",
            style="Accent.TButton",
            command=self._save_profile,
        ).grid(row=6, column=1, sticky="e", pady=12)

    @staticmethod
    def _parse_skills(text: str) -> list[str]:
        skills: list[str] = []
        seen: set[str] = set()
        for item in text.split(","):
            skill = item.strip()
            normalized = skill.casefold()
            if skill and normalized not in seen:
                skills.append(skill)
                seen.add(normalized)
        return skills

    def _save_profile(self) -> None:
        student = self._student()
        try:
            updated = self.data_manager.update_profile(
                student.student_id,
                self.profile_entries["Full name"].get(),
                self.profile_entries["Email"].get(),
                self._parse_skills(
                    self.profile_entries[
                        "Skills you can teach (comma-separated)"
                    ].get()
                ),
                self._parse_skills(
                    self.profile_entries[
                        "Skills you want to learn (comma-separated)"
                    ].get()
                ),
            )
        except (OSError, ValueError) as error:
            messagebox.showerror("Unable to save profile", str(error), parent=self.root)
            return
        self.current_student = updated
        messagebox.showinfo("Profile saved", "Your profile has been updated.", parent=self.root)
        self._show_dashboard()
        self.notebook.select(self.profile_tab)

    def _build_match_tab(self) -> None:
        tab = self.match_tab
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(2, weight=1)
        ttk.Label(
            tab,
            text="Reciprocal skill matches",
            style="Section.TLabel",
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            tab,
            text="A match can teach you a skill you want and learn a skill you teach.",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 12))

        columns = ("name", "learn", "teach")
        self.matches_table = ttk.Treeview(tab, columns=columns, show="headings")
        self.matches_table.heading("name", text="Student")
        self.matches_table.heading("learn", text="They can teach you")
        self.matches_table.heading("teach", text="You can teach them")
        self.matches_table.column("name", width=190)
        self.matches_table.column("learn", width=240)
        self.matches_table.column("teach", width=240)
        self.matches_table.grid(row=2, column=0, sticky="nsew")
        self.matches_table.bind("<Double-1>", lambda _event: self._schedule_session())

        controls = ttk.Frame(tab)
        controls.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        ttk.Button(
            controls,
            text="Find reciprocal matches",
            command=self._find_matches,
        ).pack(side="left")
        ttk.Label(controls, text="Session date (YYYY-MM-DD):").pack(
            side="left", padx=(18, 6)
        )
        self.session_date_entry = ttk.Entry(controls, width=14)
        self.session_date_entry.insert(0, date.today().isoformat())
        self.session_date_entry.pack(side="left")
        ttk.Button(
            controls,
            text="Schedule selected skill",
            style="Accent.TButton",
            command=self._schedule_session,
        ).pack(side="right")

    def _find_matches(self) -> None:
        try:
            matches = self.matcher.find_reciprocal_matches(
                self._student(),
                self.data_manager.load_students(),
            )
        except (OSError, ValueError) as error:
            messagebox.showerror("Unable to find matches", str(error), parent=self.root)
            return
        for row in self.matches_table.get_children():
            self.matches_table.delete(row)
        for match in matches:
            self.matches_table.insert(
                "",
                "end",
                iid=match.student.student_id,
                values=(
                    match.student.name,
                    ", ".join(match.they_can_teach),
                    ", ".join(match.you_can_teach),
                ),
            )
        if not matches:
            messagebox.showinfo(
                "No matches yet",
                "Add teaching and learning skills to your profile, then try again.",
                parent=self.root,
            )

    def _schedule_session(self) -> None:
        selection = self.matches_table.selection()
        if not selection:
            messagebox.showwarning(
                "Select a match",
                "Select a student from the reciprocal matches first.",
                parent=self.root,
            )
            return
        student = self._student()
        partner_id = selection[0]
        partner = self.data_manager.get_student(partner_id)
        selected_values = self.matches_table.item(partner_id, "values")
        skill = str(selected_values[1]).split(",")[0].strip()
        try:
            self.session_manager.create_session(
                teacher_id=partner.student_id,
                learner_id=student.student_id,
                skill=skill,
                session_date=self.session_date_entry.get(),
            )
        except (OSError, ValueError) as error:
            messagebox.showerror("Unable to schedule session", str(error), parent=self.root)
            return
        messagebox.showinfo(
            "Session scheduled",
            f"{partner.name} will teach you {skill}.",
            parent=self.root,
        )
        self._refresh_sessions()
        self.notebook.select(self.sessions_tab)

    def _build_search_tab(self) -> None:
        tab = self.search_tab
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(2, weight=1)
        ttk.Label(tab, text="Search by teaching skill", style="Section.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        search_row = ttk.Frame(tab)
        search_row.grid(row=1, column=0, sticky="ew", pady=12)
        self.search_entry = ttk.Entry(search_row)
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind(
            "<Return>",
            lambda _event: self._search_students(),
        )
        ttk.Button(
            search_row,
            text="Search",
            command=self._search_students,
        ).pack(side="left", padx=(8, 0))
        columns = ("name", "email", "skills")
        self.search_table = ttk.Treeview(tab, columns=columns, show="headings")
        for key, title, width in (
            ("name", "Student", 180),
            ("email", "Email", 250),
            ("skills", "Can teach", 420),
        ):
            self.search_table.heading(key, text=title)
            self.search_table.column(key, width=width)
        self.search_table.grid(row=2, column=0, sticky="nsew")

    def _search_students(self) -> None:
        try:
            results = self.matcher.search_by_skill(
                self.search_entry.get(),
                self.data_manager.load_students(),
                exclude_student_id=self._student().student_id,
            )
        except (OSError, ValueError) as error:
            messagebox.showerror("Search failed", str(error), parent=self.root)
            return
        for row in self.search_table.get_children():
            self.search_table.delete(row)
        for student in results:
            self.search_table.insert(
                "",
                "end",
                values=(
                    student.name,
                    student.email,
                    ", ".join(student.teaching_skills),
                ),
            )
        if not results:
            messagebox.showinfo(
                "No students found",
                "Try another skill or check the spelling.",
                parent=self.root,
            )

    def _build_sessions_tab(self) -> None:
        tab = self.sessions_tab
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)
        ttk.Label(tab, text="Your exchange sessions", style="Section.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 12)
        )
        columns = ("date", "skill", "partner", "role", "status", "rating")
        self.sessions_table = ttk.Treeview(tab, columns=columns, show="headings")
        headings = {
            "date": "Date",
            "skill": "Skill",
            "partner": "Other student",
            "role": "You are",
            "status": "Status",
            "rating": "Rating",
        }
        widths = {
            "date": 115,
            "skill": 170,
            "partner": 190,
            "role": 110,
            "status": 120,
            "rating": 80,
        }
        for key in columns:
            self.sessions_table.heading(key, text=headings[key])
            self.sessions_table.column(key, width=widths[key])
        self.sessions_table.grid(row=1, column=0, sticky="nsew")
        self.sessions_table.bind("<<TreeviewSelect>>", self._show_session_feedback)

        controls = ttk.Frame(tab)
        controls.grid(row=2, column=0, sticky="ew", pady=(14, 8))
        ttk.Label(controls, text="Update status:").pack(side="left")
        self.status_choice = ttk.Combobox(
            controls,
            values=("Planned", "Completed", "Cancelled"),
            state="readonly",
            width=14,
        )
        self.status_choice.set("Planned")
        self.status_choice.pack(side="left", padx=(8, 10))
        ttk.Button(
            controls,
            text="Save status",
            command=self._update_session_status,
        ).pack(side="left")

        feedback_row = ttk.Frame(tab)
        feedback_row.grid(row=3, column=0, sticky="ew")
        ttk.Label(feedback_row, text="Feedback:").pack(side="left")
        self.feedback_entry = ttk.Entry(feedback_row)
        self.feedback_entry.pack(side="left", fill="x", expand=True, padx=8)
        ttk.Label(feedback_row, text="Rating:").pack(side="left")
        self.rating_choice = ttk.Spinbox(
            feedback_row,
            from_=1,
            to=5,
            width=5,
        )
        self.rating_choice.set("5")
        self.rating_choice.pack(side="left", padx=8)
        ttk.Button(
            feedback_row,
            text="Save feedback",
            command=self._save_feedback,
        ).pack(side="left")

    def _refresh_sessions(self) -> None:
        for row in self.sessions_table.get_children():
            self.sessions_table.delete(row)
        student = self._student()
        students_by_id = {
            item.student_id: item for item in self.data_manager.load_students()
        }
        for session in self.session_manager.list_for_student(student.student_id):
            other_id = (
                session.learner_id
                if session.teacher_id == student.student_id
                else session.teacher_id
            )
            role = "Teacher" if session.teacher_id == student.student_id else "Learner"
            rating = str(session.rating) if session.rating is not None else "—"
            self.sessions_table.insert(
                "",
                "end",
                iid=session.session_id,
                values=(
                    session.session_date,
                    session.skill,
                    students_by_id[other_id].name,
                    role,
                    session.status,
                    rating,
                ),
            )

    def _selected_session(self) -> ExchangeSession | None:
        selection = self.sessions_table.selection()
        if not selection:
            messagebox.showwarning(
                "Select a session",
                "Select a session from the list first.",
                parent=self.root,
            )
            return None
        return self.session_manager.get_session(selection[0])

    def _show_session_feedback(self, _event: tk.Event) -> None:
        selection = self.sessions_table.selection()
        if not selection:
            return
        session = self.session_manager.get_session(selection[0])
        self.status_choice.set(session.status)
        self.feedback_entry.delete(0, "end")
        self.feedback_entry.insert(0, session.feedback)
        if session.rating is not None:
            self.rating_choice.set(str(session.rating))

    def _update_session_status(self) -> None:
        session = self._selected_session()
        if session is None:
            return
        try:
            self.session_manager.update_status(
                session.session_id,
                self.status_choice.get(),
            )
        except (OSError, ValueError) as error:
            messagebox.showerror("Unable to update session", str(error), parent=self.root)
            return
        self._refresh_sessions()

    def _save_feedback(self) -> None:
        session = self._selected_session()
        if session is None:
            return
        try:
            rating = int(self.rating_choice.get())
            self.session_manager.save_feedback(
                session.session_id,
                self.feedback_entry.get(),
                rating,
            )
        except (OSError, ValueError) as error:
            messagebox.showerror("Unable to save feedback", str(error), parent=self.root)
            return
        self._refresh_sessions()
        messagebox.showinfo("Feedback saved", "Thank you for your feedback.", parent=self.root)

    def _build_analytics_tab(self) -> None:
        tab = self.analytics_tab
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)
        top = ttk.Frame(tab)
        top.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(top, text="SkillSwap analytics", style="Section.TLabel").pack(side="left")
        ttk.Button(
            top,
            text="Refresh charts",
            command=self._refresh_analytics,
        ).pack(side="right")
        self.analytics_summary = tk.StringVar(value="")
        ttk.Label(tab, textvariable=self.analytics_summary, style="Subtitle.TLabel").grid(
            row=2, column=0, sticky="w", pady=(10, 0)
        )
        self.figure = Figure(figsize=(8, 4.5), dpi=100, constrained_layout=True)
        self.canvas = FigureCanvasTkAgg(self.figure, master=tab)
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")
        self._refresh_analytics()

    def _refresh_analytics(self) -> None:
        try:
            students = self.data_manager.load_students()
            sessions = self.data_manager.load_sessions()
            skill_counts = self.analytics.popular_skills(students)
            completed_count, total_count, average_rating = self.analytics.summary(
                sessions
            )
        except (OSError, ValueError) as error:
            messagebox.showerror("Unable to load analytics", str(error), parent=self.root)
            return

        self.figure.clear()
        skills_axis, sessions_axis = self.figure.subplots(1, 2)
        top_skills = skill_counts.head(8).sort_values()
        if top_skills.empty:
            skills_axis.text(0.5, 0.5, "No skills listed yet", ha="center", va="center")
            skills_axis.set_axis_off()
        else:
            skills_axis.barh(top_skills.index, top_skills.values, color="#2f855a")
            skills_axis.set_title("Popular teaching skills")
            skills_axis.set_xlabel("Student listings")
        sessions_axis.bar(
            ["Completed", "Planned", "Cancelled"],
            [
                completed_count,
                sum(item.status == "Planned" for item in sessions),
                sum(item.status == "Cancelled" for item in sessions),
            ],
            color=["#2f855a", "#3182ce", "#c05621"],
        )
        sessions_axis.set_title("Session status")
        sessions_axis.set_ylabel("Sessions")
        sessions_axis.tick_params(axis="x", rotation=12)
        self.canvas.draw()
        self.analytics_summary.set(
            f"Completed sessions: {completed_count}/{total_count}    "
            f"Average rating: {average_rating:.1f}/5"
        )

    def _student(self) -> Student:
        if self.current_student is None:
            raise RuntimeError("No student is currently logged in.")
        return self.current_student


def main() -> None:
    root = tk.Tk()
    try:
        SkillSwapApp(root)
    except (OSError, ValueError) as error:
        messagebox.showerror("Unable to start SkillSwap", str(error), parent=root)
        root.destroy()
        return
    root.mainloop()


if __name__ == "__main__":
    main()
