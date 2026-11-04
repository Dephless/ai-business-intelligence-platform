# AI Business Intelligence Platform

An API-first business intelligence platform that analyzes structured business data, calculates statistical metrics, detects potential anomalies, and generates actionable recommendations.

The platform combines deterministic analysis with optional OpenAI-powered interpretation. It is built with a modular architecture and designed to evolve into a production-oriented BI application.

## Features

- **REST API:** FastAPI endpoints with interactive OpenAPI documentation.
- **Data validation:** Pydantic request and response schemas.
- **Statistical analysis:** Numeric count, total, average, minimum, and maximum.
- **Anomaly detection:** Baseline signals for unusual and negative values.
- **AI-powered recommendations:** Optional OpenAI integration with deterministic fallback.
- **Data persistence:** SQLAlchemy ORM with PostgreSQL and SQLite support.
- **Database migrations:** Alembic-based schema versioning.
- **Containerization:** Docker and Docker Compose.
- **Automated testing:** pytest with coverage reporting.
- **Code quality:** Ruff linting and formatting, MyPy static type checking.
- **Continuous integration:** GitHub Actions workflow.

## Architecture

The application follows a modular service-oriented structure:

```text
Client
  |
  v
FastAPI REST API
  |
  v
Pydantic Validation
  |
  v
Analysis Service
  |
  +----> Statistical Analysis
  |
  +----> Baseline Recommendations
  |
  +----> Optional OpenAI Enhancement
  |
  v
SQLAlchemy ORM
  |
  v
PostgreSQL / SQLite
```

Database schema changes are managed through Alembic migrations rather than application startup table creation.

## Tech Stack

| Category | Technology |
|---|---|
| Language | Python 3.12+ |
| API | FastAPI |
| Validation | Pydantic |
| AI integration | OpenAI API |
| ORM | SQLAlchemy |
| Database | PostgreSQL, SQLite |
| Migrations | Alembic |
| Testing | pytest, pytest-cov |
| Code quality | Ruff, MyPy |
| Containerization | Docker, Docker Compose |
| CI | GitHub Actions |

## Getting Started

### Prerequisites

- Python 3.12 or newer
- Git
- Docker Desktop (for the PostgreSQL setup)

### Clone the repository

```bash
git clone https://github.com/Dephless/ai-business-intelligence-platform.git
cd ai-business-intelligence-platform
```

### Option 1: Run locally with SQLite

Create and activate a virtual environment.

**Windows PowerShell:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Create your local environment file:

```powershell
Copy-Item .env.example .env
```

For a local SQLite setup, set the following value in `.env`:

```env
DATABASE_URL=sqlite:///./business_intelligence.db
```

Apply database migrations:

```bash
alembic upgrade head
```

Start the API:

```bash
uvicorn app.main:app --reload
```

The API is available at:

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

### Option 2: Run with Docker and PostgreSQL

Create the environment file if it does not exist:

```powershell
Copy-Item .env.example .env
```

Build and start the services:

```bash
docker compose up --build -d
```

The Docker Compose setup starts:

- FastAPI application
- PostgreSQL 16 database

The API container automatically applies pending Alembic migrations before starting the application.

Check container status:

```bash
docker compose ps
```

View application logs:

```bash
docker compose logs -f api
```

Stop the services:

```bash
docker compose down
```

The PostgreSQL data is stored in a named Docker volume and is preserved when the containers are stopped. Do not use `docker compose down -v` unless you intentionally want to delete that database volume.

## Database Migrations

Alembic manages database schema changes.

Apply all pending migrations:

```bash
alembic upgrade head
```

Check the current migration:

```bash
alembic current
```

Generate a migration after changing SQLAlchemy models:

```bash
alembic revision --autogenerate -m "describe schema change"
```

Review the generated migration before applying it.

For Docker:

```bash
docker compose exec api alembic current