# AI Business Intelligence Platform

An API-first MVP that analyzes structured business data, calculates numeric metrics, and generates actionable recommendations. The application supports deterministic baseline analysis and optional OpenAI-powered interpretation.

## Features

- FastAPI REST API with interactive OpenAPI documentation
- Pydantic request/response validation
- Numeric summaries (count, total, average, min, max)
- Baseline anomaly signals and recommendations
- Optional OpenAI enhancement (disabled by default)
- SQLAlchemy persistence with PostgreSQL or local SQLite
- Docker Compose and GitHub Actions CI
- Automated API tests

## Quick start (local)

Requirements: Python 3.12+

```bash
git clone <your-repository-url>
cd ai-business-intelligence-platform
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The local default uses SQLite. Open http://localhost:8000/docs for Swagger UI.

## Run with Docker and PostgreSQL

```bash
cp .env.example .env
docker compose up --build
```

The API is available at http://localhost:8000 and Swagger UI at http://localhost:8000/docs.

## Enable OpenAI enhancement

Set `OPENAI_API_KEY` and `ENABLE_LLM=true` in `.env`. The deterministic baseline remains the fallback when LLM enhancement is disabled. Never commit `.env` or API keys.

## API

### `POST /api/v1/analyses`

Example request:

```json
{
  "dataset_name": "quarterly-sales",
  "records": [
    {"region": "North", "revenue": 12000, "cost": 7000},
    {"region": "South", "revenue": 18500, "cost": 9000},
    {"region": "West", "revenue": 9000, "cost": 6500}
  ]
}
```

Returns the persisted analysis, numeric metrics, and recommendations.

### `GET /api/v1/analyses/{analysis_id}`

Returns a previously stored analysis.

### `GET /health`

Returns service health status.

## Tests

```bash
pytest
```

## Configuration

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./business_intelligence.db` | SQLAlchemy connection URL |
| `OPENAI_API_KEY` | unset | OpenAI API key |
| `OPENAI_MODEL` | `gpt-4.1-mini` | Model used for optional enhancement |
| `ENABLE_LLM` | `false` | Enable LLM enhancement |

## Security notes

- Treat uploaded dataset content as untrusted input.
- Keep API keys in environment variables or a secret manager.
- The MVP intentionally has no public authentication layer; add authentication, authorization, rate limiting, upload limits, and audit logging before exposing it to untrusted networks.
- LLM output is validated against Pydantic schemas, but recommendations should be reviewed before operational use.
- Avoid sending personal, confidential, or regulated data to an external model without an approved data-processing basis.

## Roadmap

- [ ] Authentication and role-based access control
- [ ] Alembic migrations
- [ ] Dataset upload (CSV)
- [ ] Background processing for large datasets
- [ ] Observability and structured logging
- [ ] Evaluation dataset for recommendation quality
- [ ] Frontend dashboard

## License

MIT
