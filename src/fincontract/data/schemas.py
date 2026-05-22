from pydantic import BaseModel, Field


class AuditRequest(BaseModel):
    document_id: str = Field(..., min_length=1)
    content: str | None = None
    file_url: str | None = None


class BasisItem(BaseModel):
    doc_id: str
    title: str
    version: str
    effective_date: str
    source: str
    chunk_id: str
    excerpt: str


class Finding(BaseModel):
    rule_id: str
    message: str
    risk_score: int
    evidence: str | None = None
    basis: list[BasisItem] = []
    basis_missing: bool = False


class AuditResponse(BaseModel):
    request_id: str
    document_id: str
    risk_score: int
    risk_level: str
    findings: list[Finding]
    overall_result: str | None = None
    next_step: str | None = None
    summary: str | None = None
