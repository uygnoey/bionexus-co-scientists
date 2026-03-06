# BioNexus Co-scientists Backend

FastAPI backend for AI-powered scientific hypothesis generation.

## Quick Start

### 1. Install Dependencies

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install
```

### 2. Set Environment Variables

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Run Development Server

```bash
poetry run uvicorn app.main:app --reload
```

API will be available at http://localhost:8000

### 4. View API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Docker

```bash
cd ../infra/docker
docker-compose up
```

## API Endpoints

### Health Check
- `GET /health` - Health status

### Papers
- `GET /api/papers/search?query=quantum+computing` - Search arXiv
- `GET /api/papers/{arxiv_id}` - Get specific paper

### Hypotheses
- `POST /api/hypotheses/generate` - Generate hypotheses

Example request:
```json
{
  "paper_ids": ["2301.12345", "2302.67890"],
  "max_hypotheses": 5,
  "debate_rounds": 3,
  "clustering": true
}
```

## Development

### Run Tests

```bash
poetry run pytest
```

### Code Quality

```bash
poetry run black app/
poetry run isort app/
poetry run mypy app/
```

## Architecture

```
app/
├── agents/          # Claude Agent SDK multi-agent system
├── arxiv/           # arXiv integration
├── rag/             # RAG system (Qdrant + Neo4j)
├── api/             # FastAPI routers
├── models/          # Pydantic data models
└── core/            # Configuration & logging
```
