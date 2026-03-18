# The Clinic App — Demo Application

A fictional SaaS clinic appointment management platform built to demonstrate realistic QA/SDET test scenarios. Used as the **system under test** for [the-clinic-playwright](https://github.com/daliborpavlovski/the-clinic-playwright).

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI 0.111 + Python 3.11 |
| ORM | SQLAlchemy 2.0 + Alembic migrations |
| Database | PostgreSQL 16 |
| Auth | JWT (python-jose) + bcrypt |
| Frontend | Vanilla HTML/CSS/JS (no framework) |
| Serving | nginx (reverse proxy + static) |
| Container | Docker + Docker Compose |

## Quick Start

```bash
# Start all services
make up

# Seed with test users
make seed

# Access the app
open http://localhost         # Frontend
open http://localhost/docs    # Swagger UI
```

## Seed Credentials

| Role | Email | Password |
|---|---|---|
| Admin | `admin@theclinicapp.com` | `Admin1234!` |
| Doctor | `doctor@theclinicapp.com` | `Doctor1234!` |
| Patient | `patient@theclinicapp.com` | `Patient1234!` |

## API Surface (`/api/v1`)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register new user (201 / 409 / 422) |
| POST | `/auth/login` | Login → JWT tokens (200 / 401) |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/logout` | Logout (stateless) |
| GET/PUT | `/users/me` | Current user profile |
| GET | `/users` | List all users (admin only) |
| DELETE | `/users/{id}` | Deactivate user (admin only) |
| GET/POST | `/appointments` | List / create appointments |
| GET/PUT/DELETE | `/appointments/{id}` | Manage appointment |
| PATCH | `/appointments/{id}/status` | Status machine transition |
| GET | `/doctors` | List doctor profiles |
| GET | `/doctors/{id}` | Doctor profile |
| GET | `/doctors/{id}/slots` | Available booking slots |
| PUT | `/doctors/{id}/profile` | Update doctor profile |

## Business Rules (drive test scenarios)

- **Status machine:** `pending → confirmed → completed` or `pending/confirmed → cancelled`
- **No double-booking:** Patient or doctor cannot have two appointments at overlapping slots → 409
- **Future slots only:** Cannot book in the past → 400
- **Cancel restriction:** Cannot cancel within 1 hour of start time → 400
- **RBAC:** Patients see only their own appointments; doctors only their own; admins see all
- **Password policy:** Minimum 8 characters, at least one digit
- **Profile access:** Doctors can only edit their own profile

## Makefile Commands

```bash
make up          # Start all services + run migrations
make down        # Stop all services
make seed        # Seed database with test users
make migrate     # Run Alembic migrations
make logs        # Tail all logs
make test        # Run backend unit tests
make clean       # Remove volumes and containers
```

## Architecture

```
Browser → nginx:80
            ├── /api/* → FastAPI:8000
            ├── /docs  → Swagger UI (proxied)
            └── /*     → Static frontend files
```
