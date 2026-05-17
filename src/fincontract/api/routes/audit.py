from fastapi import APIRouter, HTTPException

from fincontract.core.errors import AuditError
from fincontract.data.schemas import AuditRequest, AuditResponse
from fincontract.services.audit_service import audit_document

router = APIRouter()


@router.post("/", response_model=AuditResponse)
def audit(request: AuditRequest) -> AuditResponse:
    try:
        return audit_document(request)
    except AuditError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
