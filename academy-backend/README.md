# Academy backend

Phases 1 through 3 provide the Flask application factory, configuration,
extensions, portable SQLAlchemy models, response/error handling, migration
integration, static frontend serving, health endpoint, JWT authentication,
database-backed logout revocation, password changes/resets, account lockout,
reusable role guards, core users/staff/courses/batches/students APIs, and
attendance/assessment/marks APIs with trainer ownership and student isolation.
It also includes fee plans, installments, payments, receipt sequencing, voids,
dues, and student fee summaries.

## Setup

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
flask db init
flask db migrate -m "Initial schema"
flask db upgrade
flask run
```

The default SQLite database is `academy.db`. For MySQL, install the
`PyMySQL` dependency and set `DATABASE_URL` to a SQLAlchemy URL such as
`mysql+pymysql://root:password@localhost:3306/academy_db`. Set
`DATABASE_URL` to a PostgreSQL URL for production when applicable. The existing frontend is served from
`FRONTEND_DIR` (default `../login-page`).

## Verify

```powershell
pytest
```

The next phase will add business services and operational APIs. The unresolved
provider decisions from the frontend audit remain intentionally outside this
phase.

## Demo seed

After applying migrations, run `flask seed`. The command is idempotent and is
refused in production. It creates the demo users, courses, batches, students,
fee plans, leads, companies, and placement drives listed in the command output.

## API documentation

The current endpoint overview is in [docs/openapi.yaml](./docs/openapi.yaml).
The frontend audit and detailed contract are in the repository-level `docs/`
directory.

## Delivery status

The backend API phases and focused tests are complete. The shared frontend
authentication and shell integration is wired, while individual page renderers
still require endpoint-by-endpoint replacement of their prototype sample
arrays. Those UI data-source migrations should be completed before production
release.
