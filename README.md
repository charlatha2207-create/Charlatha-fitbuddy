# FitBuddy – AI Fitness Plan Generator

FitBuddy is a FastAPI + Jinja2 + SQLite web application using Google's Gemini API to generate personalized 7-day workout plans, nutrition/recovery tips, and revised plans from feedback.

## Features

- User profile: name, user ID, age, weight, goal, intensity.
- AI-generated 7-day workout plan.
- AI-generated nutrition/recovery tip.
- Feedback-based plan regeneration.
- SQLite + SQLAlchemy persistence.
- Admin login and dashboard.
- JSON REST API.
- Health endpoint.
- Input validation and friendly error pages.
- Gemini key stored in `.env`.

## Project structure

```text
FitBuddy/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── ai_service.py
│   ├── gemini_generator.py
│   ├── gemini_flash_generator.py
│   ├── updated_plan.py
│   ├── routes.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── result.html
│   │   ├── admin_login.html
│   │   ├── all_users.html
│   │   └── error.html
│   └── static/
│       ├── css/style.css
│       └── js/app.js
├── tests/
│   ├── conftest.py
│   └── test_app.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## VS Code setup

### Windows

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your Gemini API key:

```env
GEMINI_API_KEY=your_real_key
```

Run:

```powershell
uvicorn app.main:app --reload
```

Open:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/health

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Admin

Open:

```text
http://127.0.0.1:8000/admin/login
```

Use the values in `.env`. Change the default password before using the app outside local development.

Dashboard:

```text
http://127.0.0.1:8000/view-all-users
```

## REST API

### POST `/api/v1/plans`

```json
{
  "user_id": "U1001",
  "name": "Alex",
  "age": 24,
  "weight": 70,
  "goal": "muscle gain",
  "intensity": "medium"
}
```

### GET `/api/v1/users/U1001`

### POST `/api/v1/plans/U1001/feedback`

```json
{
  "feedback": "Add more cardio and one additional rest day."
}
```

### GET `/api/v1/users`

### GET `/health`

## Tests

The test suite mocks Gemini, so a real API key is not required:

```powershell
pytest -q
```

## Gemini model configuration

The model IDs are environment variables:

```env
GEMINI_WORKOUT_MODEL=gemini-3.8-flash
GEMINI_TIP_MODEL=gemini-3.8-flash
```

This keeps model selection outside the application code.

## Safety

FitBuddy is a wellness-planning demonstration, not a medical diagnosis or treatment system. AI-generated exercise and nutrition content should be reviewed by an appropriate qualified professional for injuries, chronic conditions, pregnancy-related needs, eating-disorder concerns, or other medical considerations.
