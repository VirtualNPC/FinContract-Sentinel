from fincontract.data.schemas import AuditRequest
from fincontract.services.audit_service import audit_document
from fincontract.workers.celery_app import celery_app


@celery_app.task(name="fincontract.workers.tasks.audit_document")
def audit_document_task(payload: dict) -> dict:
    request = AuditRequest(**payload)
    response = audit_document(request)
    return response.model_dump()
