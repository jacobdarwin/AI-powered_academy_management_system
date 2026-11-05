# Academy Management System

An academy management system for handling admissions, users, students, staff,
attendance, academics, fees, and placements from one role-based web
application.

The project contains:

- A Flask REST API and database layer in [`academy-backend/`](./academy-backend/)
- A static HTML, CSS, and JavaScript frontend in [`login-page/`](./login-page/)
- Database migrations, automated tests, and QA documentation
- A Windows one-click launcher in [`start-academy.bat`](./start-academy.bat)

## Features

### Role-based access

- **Super Admin**: manage users, branches, courses, batches, fees, expenses,
  reports, and system settings.
- **Staff**: access assigned operational workflows such as students,
  attendance, academics, counseling, accounts, or placements according to
  their permissions.
- **Student**: view dashboard information, timetable, attendance, fees,
  marks, study materials, placements, certificates, and profile information.

### Core modules

- Authentication, JWT access tokens, refresh tokens, logout revocation, and
  password reset flows
- User and student management
- Courses, batches, trainers, and timetable data
- Attendance, assessments, marks, and assignments
- Fee plans, installments, payments, receipts, dues, and expenses
- Leads, companies, placement drives, and applications
- Announcements, notifications, study materials, and certificates
- API validation, role guards, object-level access checks, and error handling

### AI, ML, deep learning, and LLM roadmap

The application includes the user-facing foundation for intelligent academy
features:

- **AI assistant**: students can ask questions about attendance, fees,
  classes, deadlines, and placement drives through the assistant interface.
- **Machine learning analytics**: the Super Admin area includes a course-demand
  forecast view designed to use historical admission data.
- **Deep-learning extensions**: the platform can be extended with models for
  student performance prediction, dropout-risk analysis, attendance patterns,
  and personalized learning recommendations.
- **LLM integration**: the assistant can be connected to a hosted or
  self-hosted large language model for natural-language answers, summaries,
  academic guidance, and staff productivity workflows.

The current forecast screen uses a demo trend calculation and the assistant
uses the backend assistant endpoint. Production ML, deep-learning, and LLM
deployments require a selected model provider, real training data, privacy
controls, evaluation, monitoring, and separate production configuration.

## Screenshots

### Sign-in

![Academy sign-in screen](./docs/images/sign-in.png)

### Student dashboard

![Student dashboard](./docs/images/student-dashboard.png)

## Technology stack

### Backend

- Python 3.11+
- Flask
- SQLAlchemy and Flask-Migrate/Alembic
- JWT authentication with Flask-JWT-Extended
- SQLite for local development
- MySQL or PostgreSQL support through SQLAlchemy
- Pytest and pytest-flask

### Frontend

- HTML5
- CSS3
- Vanilla JavaScript
- Fetch API
- Same-origin API requests when served by Flask

## Project structure

```text
.
├── academy-backend/
│   ├── app/                 # Flask application, models, API routes, auth
│   ├── migrations/          # Alembic database migrations
│   ├── tests/               # Backend and security/business-rule tests
│   ├── docs/openapi.yaml    # API endpoint overview
│   ├── .env.example         # Safe environment-variable template
│   └── README.md            # Backend-specific documentation
├── login-page/
│   ├── assets/js/           # Shared API client and page scripts
│   ├── staff/               # Staff pages
│   ├── student/             # Student pages
│   └── superadmin/          # Super Admin pages
├── docs/images/             # README screenshots
├── qa/                      # QA inventory, reports, defects, traceability
├── start-academy.bat        # Windows launcher
└── README.md
```

## Requirements

- Windows with Python installed and available through the `py` command
- Python 3.11 or newer
- Git
- MySQL 8+ if using MySQL instead of the default SQLite database

## Quick start on Windows

The easiest way to run the application is:

1. Clone the repository.
2. Double-click [`start-academy.bat`](./start-academy.bat).
3. Open `http://127.0.0.1:5000/` if the browser does not open automatically.

The launcher starts Flask on `127.0.0.1:5000`. Flask serves both the frontend
and the `/api/v1` backend from the same origin.

### Manual setup

From PowerShell:

```powershell
cd academy-backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

For a new local database, apply the migrations:

```powershell
flask --app wsgi.py db upgrade
```

Start the server:

```powershell
py -m flask --app wsgi.py run --host 127.0.0.1 --port 5000
```

Then visit `http://127.0.0.1:5000/`.

## Environment configuration

Copy `academy-backend/.env.example` to `academy-backend/.env` and update the
values for the local machine. Never commit `.env`; it can contain database
passwords and application secrets.

Example SQLite configuration:

```dotenv
FLASK_APP=wsgi.py
FLASK_ENV=development
SECRET_KEY=replace-with-a-long-random-value
JWT_SECRET_KEY=replace-with-another-long-random-value
DATABASE_URL=sqlite:///academy.db
FRONTEND_DIR=../login-page
MAX_CONTENT_LENGTH=16777216
```

### MySQL configuration

Create the database first, then set a SQLAlchemy connection URL:

```dotenv
DATABASE_URL=mysql+pymysql://academy_user:your_password@127.0.0.1:3306/academy_db
```

Apply migrations after configuring the connection:

```powershell
flask --app wsgi.py db upgrade
```

Do not place real passwords, production keys, or personal account credentials
in this README or in source control.

## Login and account setup

The login screen supports Super Admin, Staff, and Student roles. Select the
appropriate role and use the email or login ID assigned by the academy.

For a fresh local installation, create accounts through the backend's approved
administrative workflow or a protected local seed process. Do not publish
working passwords in the repository. Change any temporary development
password immediately after the first login.

## API

The API is available under:

```text
http://127.0.0.1:5000/api/v1
```

The endpoint overview is documented in
[`academy-backend/docs/openapi.yaml`](./academy-backend/docs/openapi.yaml).
Authentication-protected requests use the access token returned by the login
endpoint. The shared frontend client in
[`login-page/assets/js/api.js`](./login-page/assets/js/api.js) manages token
storage, refresh, logout, and API error handling.

Useful health check:

```text
GET /api/v1/health
```

## Testing

Install the backend dependencies, activate the virtual environment, and run:

```powershell
cd academy-backend
.\.venv\Scripts\Activate.ps1
pytest
```

The tests cover authentication, authorization, route-role expectations,
student data isolation, trainer ownership, fee rules, receipt sequencing,
placement eligibility, and other business constraints.

## Database migrations

Use Flask-Migrate for schema changes:

```powershell
cd academy-backend
flask --app wsgi.py db upgrade
flask --app wsgi.py db current
flask --app wsgi.py db check
```

When changing models during development:

```powershell
flask --app wsgi.py db migrate -m "Describe the schema change"
flask --app wsgi.py db upgrade
```

Review generated migrations before applying them to a shared or production
database.

## Troubleshooting

### Browser shows repeated 401 responses

Stop the server, clear the browser's site data for `127.0.0.1`, restart the
application, and sign in again. This usually means the browser has an expired
or revoked token.

### Port 5000 is already in use

Close the process using port 5000, or run Flask on another port and open that
port in the browser:

```powershell
py -m flask --app wsgi.py run --host 127.0.0.1 --port 5001
```

### MySQL connection fails

Check that MySQL is running, the database exists, the username and password are
correct, and `DATABASE_URL` starts with `mysql+pymysql://`. Then run
`flask --app wsgi.py db upgrade` again.

### Frontend changes are not visible

Hard-refresh the browser with `Ctrl+F5`. Confirm that the backend's
`FRONTEND_DIR` points to the repository's `login-page` directory.

## Security notes

- Keep `.env`, database files, uploads, tokens, and private keys out of Git.
- Use long, random `SECRET_KEY` and `JWT_SECRET_KEY` values.
- Use HTTPS and secure cookie/token settings in production.
- Do not use demo or temporary passwords in a public deployment.
- Review authorization and QA reports before production release.

## Documentation

- [Backend setup and API notes](./academy-backend/README.md)
- [OpenAPI endpoint overview](./academy-backend/docs/openapi.yaml)
- [QA inventory](./qa/inventory.md)
- [QA test report](./qa/test-report.md)
- [Known defects](./qa/defects.md)
- [Changelog](./CHANGELOG.md)

## License

No license has been declared yet. Add a license file before distributing the
project publicly.
