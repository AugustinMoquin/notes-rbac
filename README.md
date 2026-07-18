# notes-rbac

[![CI](https://github.com/AugustinMoquin/notes-rbac/actions/workflows/ci.yml/badge.svg)](https://github.com/AugustinMoquin/notes-rbac/actions/workflows/ci.yml)

A multi-tenant notes API built with FastAPI. Users belong to a tenant
(organization), authenticate with JWTs, and are subject to role-based access
control. Tenants are fully isolated from one another.

## Model

- **Signup** creates a new tenant and its first user as an `admin`.
- **Admins** can add users to their tenant and edit/delete any note in it.
- **Members** can create notes and edit/delete their own.
- A user in one tenant can never see or touch another tenant's data — cross-tenant
  access returns `404`, not `403`, so tenants can't probe each other's ids.

Persistence is SQLAlchemy; it runs on Postgres in production and SQLite in tests.

## Endpoints

| Method | Path              | Access        | Description                    |
| ------ | ----------------- | ------------- | ------------------------------ |
| POST   | `/auth/signup`    | public        | Create tenant + admin, get JWT |
| POST   | `/auth/login`     | public        | Get JWT                        |
| GET    | `/auth/me`        | authenticated | Current user                   |
| POST   | `/users`          | admin         | Add a user to the tenant       |
| GET    | `/users`          | admin         | List tenant users              |
| POST   | `/notes`          | authenticated | Create a note                  |
| GET    | `/notes`          | authenticated | List tenant notes              |
| GET    | `/notes/{id}`     | authenticated | Get a note (own tenant)        |
| PUT    | `/notes/{id}`     | owner or admin | Update a note                 |
| DELETE | `/notes/{id}`     | owner or admin | Delete a note                 |

## Run

```sh
docker compose up -d          # Postgres on :5433
DATABASE_URL=postgresql+psycopg://notes:notes@localhost:5433/notes \
  uvicorn app.main:app --reload
```

Interactive docs at `http://localhost:8000/docs`.

## Test

```sh
python -m venv .venv && . .venv/Scripts/activate   # or bin/activate on unix
pip install -r requirements-dev.txt
pytest                                              # runs on in-memory SQLite
```

## Config

| Env                           | Default                 |
| ----------------------------- | ----------------------- |
| `DATABASE_URL`                | `sqlite:///./notes.db`  |
| `JWT_SECRET`                  | `dev-secret-change-me`  |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60`                    |
