# Technology Selection - FinContract Sentinel

## Decision summary
- Language: Python 3.11 (3.10+ supported)
- API framework: FastAPI
- LLM orchestration: LangChain 0.2
- Vector store: Chroma for dev, Pinecone for prod
- Relational DB: PostgreSQL 15 + pgvector
- Cache: Redis 7
- Task queue: Celery
- OCR: Aliyun OCR primary, Tencent OCR fallback (configurable)
- Document parsing: pdfplumber, PyPDF2, pdf2image, pandas, openpyxl
- Observability: OpenTelemetry + Prometheus + Grafana; structured logging via structlog
- Containerization: Docker + Docker Compose
- CI/CD: GitHub Actions

## Rationale
- Python ecosystem is strongest for OCR, document parsing, and LLM integration.
- FastAPI provides high performance and auto-generated API docs.
- PostgreSQL + pgvector supports structured data and embeddings with strong auditability.
- Celery + Redis supports async OCR and batch audit workflows.
- Chroma is lightweight for local dev; Pinecone scales for production.

## Alternatives and tradeoffs
- Vector store: Qdrant can replace Pinecone for self-hosted deployments.
- OCR: PaddleOCR can be a local fallback when cloud OCR is unavailable.
- Task queue: RabbitMQ can replace Redis if advanced routing is needed.

## Open decisions
- Cloud provider and region selection.
- OCR vendor contract and data residency constraints.
- Production vector store choice (managed vs self-hosted).
