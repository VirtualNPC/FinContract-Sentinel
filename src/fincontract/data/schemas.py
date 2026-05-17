from pydantic import BaseModel, Field


class AuditRequest(BaseModel):
    document_id: str = Field(..., min_length=1)
    content: str | None = None
    file_url: str | None = None


class Finding(BaseModel):
    rule_id: str
    message: str
    risk_score: int
    evidence: str | None = None


class AuditResponse(BaseModel):
    request_id: str
    document_id: str
    risk_score: int
    risk_level: str
    findings: list[Finding]
