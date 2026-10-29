# SkillSwap — Student Skill Exchange Platform

SkillSwap is a Python desktop mini project. Students can share teaching and
learning skills, find reciprocal partners, schedule sessions, track progress,
and review simple analytics.

## Requirements

- Python 3.10 or later
- Tkinter (included with most Windows Python installations)
- NumPy
- Pandas
- Matplotlib

The app uses JSON files for storage. It does not use a SQL database, a web
framework, HTML, CSS, JavaScript, or external APIs.

## Run on Windows

Open PowerShell in this project folder and run:

```powershell
python -m pip install numpy pandas matplotlib
python app.py
```

The first launch creates `data\students.json` and `data\sessions.json` with
sample records for these four students:

- `sakshu@example.com`
- `vaishnavi@example.com`
- `anjali@example.com`
- `revati@example.com`

On a fresh install, all four sample accounts use the password `skill123`.
For an existing project, Anjali's previously registered password is preserved;
the other demo accounts use `skill123`. These accounts are for demonstration
only; do not use this prototype to store real student passwords or sensitive
data.
Sample profiles have reciprocal skill matches and sessions, including completed
sessions with ratings and upcoming planned sessions.

## Features

1. Register and log in with email and password.
2. Edit a student name, email, teaching skills, and learning skills.
3. Search other students by a teaching skill.
4. Find reciprocal matches: each student can teach something the other wants
   to learn.
5. Schedule a dated teaching session with a matched partner.
6. Track sessions as Planned, Completed, or Cancelled.
7. Leave feedback and a 1–5 rating for a completed session.
8. View popular teaching skills and session-status charts.

## Data files

- `data\students.json` — student profiles and salted password hashes.
- `data\sessions.json` — session details, status, feedback, and ratings.

Keep a backup before manually editing these files. If an existing first-step
`students.json` is found without login fields, the app adds demo credentials
without deleting its profile and skill information. The initial password for
those migrated demo profiles is `skill123`.

## Run tests

```powershell
python -m unittest discover -s tests -v
```

Tests use temporary JSON files and do not modify the app's sample data.

## सोप्या मराठीत — प्रोजेक्ट कसा वापरायचा

1. PowerShell मध्ये प्रोजेक्ट फोल्डर उघडा आणि वरच्या दोन कमांड चालवा.
2. Demo email आणि `skill123` वापरून login करा किंवा **Create account** निवडा.
3. **My profile** मध्ये शिकवता येणारी आणि शिकायची कौशल्ये comma ने वेगळी
   लिहून **Save profile** दाबा. कौशल्य जोडण्यासाठी यादीत लिहा, बदलण्यासाठी
   त्याचा मजकूर बदला, आणि काढण्यासाठी तो मजकूर पुसा.
4. **Skill matches** मध्ये परस्पर कौशल्य जुळवणी शोधा. जोडी निवडून तारीख
   टाकल्यावर session ठरवा.
5. **Sessions** मध्ये session पूर्ण किंवा रद्द करा. पूर्ण झालेल्या session ला
   feedback आणि 1 ते 5 rating देता येते.
6. **Search students** आणि **Analytics** tabs मधून शोध व आलेख पहा.
7. बदल केले तर ते `data` फोल्डरमधील JSON फाइलमध्ये जतन होतात.

चाचण्या चालवण्यासाठी:

```powershell
python -m unittest discover -s tests -v
```
