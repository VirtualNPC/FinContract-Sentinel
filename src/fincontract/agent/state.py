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
