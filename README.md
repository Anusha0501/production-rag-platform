# Production RAG Platform

A portfolio-grade Retrieval-Augmented Generation platform for AI Engineer interview preparation and real-world product practice.

## Architecture

- **Frontend:** React/Vite chat, auth, uploads, history, evaluation dashboard.
- **Backend:** FastAPI clean architecture layers: `api`, `domain`, `repositories`, `services`, `schemas`, `core`.
- **Data:** PostgreSQL stores users, document metadata, conversations, and messages.
- **Vector DB:** ChromaDB stores chunked PDF content for retrieval.
- **Monitoring:** LangSmith tracing wraps the RAG answer path.
- **Delivery:** Docker Compose locally, GitHub Actions CI, Render blueprint for deployment.

## Quickstart

```bash
cp .env.example .env
docker compose up --build
```

Open the frontend at <http://localhost:3000> and the API docs at <http://localhost:8000/docs>.

## Production Deployment

1. Push this repository to GitHub.
2. Create a Render Blueprint from `render.yaml`.
3. Set secrets: `JWT_SECRET`, `OPENAI_API_KEY`, `LANGSMITH_API_KEY`.
4. Restrict CORS origins in `backend/app/main.py` to the deployed frontend URL.
5. Add backups and retention policies for PostgreSQL and Chroma volumes.

## Security Checklist

- Hash passwords with bcrypt and issue short-lived JWTs.
- Validate upload content type and add file-size limits at the proxy/API layer.
- Store secrets only in Render/GitHub secret managers.
- Use per-user vector collections to isolate tenant data.
- Add rate limiting and audit logs before public launch.

## Scaling Notes

- Run FastAPI with multiple workers behind Render's load balancer.
- Move uploads to object storage for large documents.
- Use managed Postgres with read replicas for analytics-heavy dashboards.
- Batch embedding jobs through a queue for high-volume ingestion.
- Cache frequent retrievals and evaluation metrics.

## Interview Teaching Map

- **System design:** Explain the request flow from browser to FastAPI, PostgreSQL, Chroma, and LangSmith.
- **Clean architecture:** Keep framework code in `api`, business logic in `services`, persistence in `repositories`, and entities in `domain`.
- **Production deployment:** Discuss Docker images, health checks, secrets, migrations, CI gates, and rollback plans.
- **Scaling:** Cover ingestion queues, vector sharding, observability, async workers, and cost controls.
- **Security:** Cover auth, tenant isolation, prompt-injection mitigation, PDF scanning, CORS, and least-privilege secrets.

## API Highlights

- `POST /api/auth/register` and `POST /api/auth/login`
- `POST /api/documents` for PDF ingestion
- `POST /api/chat` for RAG chat
- `GET /api/conversations` for history
- `GET /api/evaluations` for dashboard metrics
