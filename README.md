# FinContract Sentinel

AI-assisted financial and contract audit agent focused on explainable results.

## Features
- Multi-format parsing (PDF, Word, Excel, image)
- Rule engine plus LLM reasoning
- Risk scoring with human-in-the-loop review
- Audit logs and traceability

## Quick start (local)
1) python -m venv .venv
2) .\.venv\Scripts\activate
3) pip install -e .
4) copy .env.example to .env and fill values
5) uvicorn fincontract.api.main:app --reload

## Worker
celery -A fincontract.workers.celery_app.celery_app worker -l INFO

## Tests
pytest

## Project layout
- src/fincontract/api: FastAPI routes
- src/fincontract/agent: orchestration pipeline
- src/fincontract/tools: OCR, vector store, and rule engine adapters
- src/fincontract/services: business services
- src/fincontract/workers: async tasks
- src/fincontract/rules: rule definitions
