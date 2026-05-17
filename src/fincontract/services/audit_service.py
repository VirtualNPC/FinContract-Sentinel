from fincontract.agent.pipeline import run_audit
from fincontract.data.schemas import AuditRequest, AuditResponse, Finding


def audit_document(request: AuditRequest) -> AuditResponse:
    state = run_audit(request.document_id, request.content, request.file_url)
    findings = [Finding(**item) for item in state.findings]

    return AuditResponse(
        request_id=state.request_id,
        document_id=state.document_id,
        risk_score=state.risk_score or 0,
        risk_level=state.risk_level or "low",
        findings=findings,
    )
