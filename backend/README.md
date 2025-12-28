# PetHope Backend

FastAPI backend for the PetHope pet adoption platform.

## Setup

### Environment Variables

Copy `.env.example` from the project root and configure:

```bash
# From project root
cp .env.example .env
```

### Running with Docker

```bash
# From project root
docker compose up -d backend
```

### Running Locally (without Docker)

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

## Database Migrations

### Run Migrations

```bash
# Inside container
docker compose exec backend alembic upgrade head

# Or locally
alembic upgrade head
```

### Create New Migration

```bash
# Auto-generate from model changes
docker compose exec backend alembic revision --autogenerate -m "description"

# Or create empty migration
docker compose exec backend alembic revision -m "description"
```

### Rollback Migration

```bash
# Rollback one version
docker compose exec backend alembic downgrade -1

# Rollback to specific version
docker compose exec backend alembic downgrade <revision>

# Rollback all
docker compose exec backend alembic downgrade base
```

### View Migration History

```bash
docker compose exec backend alembic history
docker compose exec backend alembic current
```

## API Documentation

Once running, visit:

- **Swagger UI**: http://localhost/docs
- **ReDoc**: http://localhost/redoc
- **OpenAPI JSON**: http://localhost/openapi.json

## Project Structure

```
backend/
├── alembic/              # Database migrations
│   ├── versions/         # Migration scripts
│   ├── env.py           # Alembic environment
│   └── script.py.mako   # Migration template
├── app/
│   ├── main.py          # FastAPI application
│   ├── config.py        # Settings management
│   ├── database.py      # Database connection
│   ├── models/          # SQLAlchemy models
│   │   ├── animal.py
│   │   ├── image.py
│   │   └── base.py
│   ├── schemas/         # Pydantic schemas
│   │   ├── animal.py
│   │   ├── image.py
│   │   └── common.py
│   ├── routers/         # API endpoints
│   └── services/        # Business logic
│       └── storage.py
├── alembic.ini          # Alembic configuration
├── requirements.txt     # Python dependencies
└── Dockerfile          # Production image
```

## Development

### Code Style

- Use type hints for all functions
- Follow PEP 8
- Use async/await for all database operations
- Validate input with Pydantic schemas

### Testing

```bash
# Run tests (when implemented)
docker compose exec backend pytest
```

## Health Check

```bash
curl http://localhost/health
```

Returns:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "development",
  "checks": {
    "database": "healthy",
    "storage": "healthy"
  }
}
```
