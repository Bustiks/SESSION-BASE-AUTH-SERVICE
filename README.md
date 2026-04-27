# Session-based Auth Service

A small session-based authentication API built as a learning / portfolio project. It exposes registration, login, logout, and profile flows, persists users in PostgreSQL, and manages sessions via Redis with HttpOnly cookies.

## Features

- User registration with email validation and hashed passwords (pwdlib)
- Login with email + password; session stored in Redis with a 7-day TTL
- Logout that revokes the session immediately
- Protected `/me` endpoint requiring a valid session cookie
- Async stack: FastAPI + SQLAlchemy 2 + asyncpg + redis-py
- Database migrations with Alembic
- Structured logging (colored console + rotating files) with sensitive-data filtering
- Docker Compose for local Postgres + Redis + API with hot reload

## Tech stack

| Layer | Choice |
|---|---|
| Framework | FastAPI |
| ORM | SQLAlchemy 2 (async) |
| Database | PostgreSQL 16 |
| Session store | Redis 7 |
| Password hashing | pwdlib |
| Config | pydantic-settings, .env |
| Migrations | Alembic |

## API overview

Base path: `/api`

| Method | Path | Auth required | Description |
|---|---|---|---|
| POST | `/api/auth/registration` | No | Create account; sets session cookie |
| POST | `/api/auth/login` | No | Authenticate; sets session cookie |
| POST | `/api/auth/logout` | Yes | Revoke session; clears cookie |
| GET | `/api/user/me` | Yes | Return current user profile |

Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI).

## How sessions work

1. On login or registration the server generates a UUID, writes `session:{uuid} → user_id` in Redis (TTL 7 days), and sets an HttpOnly cookie (`petservice_session`) with that UUID.
2. On every protected request `get_current_user` reads the cookie, looks up the UUID in Redis, and fetches the user from Postgres.
3. Logout deletes the Redis key and clears the cookie — the session is immediately invalid.

No JWT signatures, no token refresh dance — the server is the source of truth.

## Prerequisites

- Python 3.12+ (see [Dockerfile](Dockerfile))
- Docker & Docker Compose (recommended), or local PostgreSQL + Redis instances

## Environment variables

Create a `.env` file in the project root (never commit real secrets):

| Variable | Description |
|---|---|
| `DB_HOST` | Database host (`localhost` locally; `postgres` in Compose) |
| `DB_PORT` | Database port (e.g. `5432`) |
| `DB_USER` | Database user |
| `DB_PASS` | Database password |
| `DB_NAME` | Database name |
| `REDIS_HOST` | Redis host (`localhost` locally; `redis` in Compose) |
| `REDIS_PORT` | Redis port (e.g. `6379`) |
| `REDIS_DB` | Redis logical DB index (e.g. `0`) |
| `SESSION_COOKIE_NAME` | Cookie name for the session token |
| `SESSION_TTL_SECONDS` | Session lifetime in seconds (default `604800` — 7 days) |
| `SECRET_KEY` | Secret used for internal operations — use a long, random value |

Example (align credentials with [docker-compose.yaml](docker-compose.yaml) if you use the default services):

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASS=postgres
DB_NAME=AuthServiceDB

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

SESSION_COOKIE_NAME=petservice_session
SESSION_TTL_SECONDS=604800

SECRET_KEY=change-me-to-a-long-random-string
```

## Quick start (Docker Compose)

From the repository root:

```bash
docker compose up --build
```

- API: [http://localhost:8000](http://localhost:8000)
- Postgres is exposed on `localhost:5432`
- Redis is exposed on `localhost:6379`

Apply migrations once (with the stack running):

```bash
docker compose exec backend alembic upgrade head
```

Then open `/docs` and try the auth endpoints.

## Local development (without Docker)

Create a virtual environment and install dependencies:

```bash
python -m venv venv
.\venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

Ensure PostgreSQL and Redis are running and match your `.env`.

Run migrations:

```bash
alembic upgrade head
```

Start the app (from the project root so `src` imports resolve):

```bash
uvicorn src.main:app --reload --reload-dir src
```

## Tests

```bash
pytest src/tests -v
```

Tests use an in-memory SQLite database and `fakeredis` — no running Postgres or Redis instance required.

## Project layout

```
├── alembic/              # migration scripts
├── src/
│   ├── api/              # HTTP routes (auth, user)
│   ├── database/         # engine, session, Redis client, settings
│   ├── models/           # SQLAlchemy models
│   ├── repository/       # data access layer
│   ├── schemas/          # Pydantic request / response models
│   ├── services/         # business logic
│   ├── utils/            # dependencies, logging, annotated types
│   ├── tests/
│   └── main.py
├── docker-compose.yaml
├── Dockerfile
├── logging_config.yaml
└── requirements.txt
```

## Security notes

This is a pet / portfolio service: there is no rate limiting, CSRF protection, or OAuth — only server-side sessions backed by Redis.

- Use a strong `SECRET_KEY` and HTTPS in any shared environment.
- CORS is restricted to local development origins in [src/main.py](src/main.py); update it for real front-end domains.
- Session cookies are HttpOnly — JavaScript cannot read them — but `Secure` should be enforced in production (HTTPS only).
