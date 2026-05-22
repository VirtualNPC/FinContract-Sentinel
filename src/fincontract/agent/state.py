from dataclasses import dataclass, field


@dataclass
class AuditState:
    request_id: str
    document_id: str
    raw_content: str | None
    extracted_text: str | None = None
    findings: list[dict] = field(default_factory=list)
    risk_score: int | None = None
    risk_level: str | None = None
    overall_result: str | None = None
    next_step: str | None = None
    summary: str | None = None
    needs_human_review: bool = False
