from uuid import uuid4

import structlog

from fincontract.agent.state import AuditState
from fincontract.core.errors import ParseError
from fincontract.tools.ocr import OCRClient
from fincontract.tools.rule_engine import RuleEngine

log = structlog.get_logger()


def run_audit(document_id: str, content: str | None, file_url: str | None) -> AuditState:
    state = AuditState(request_id=str(uuid4()), document_id=document_id, raw_content=content)

    text = (content or "").strip()
    if not text and file_url:
        text = OCRClient().extract_text(file_url)

    if not text:
        raise ParseError("No content to audit.")

    state.extracted_text = text
    rule_engine = RuleEngine()
    state.findings = rule_engine.evaluate(text)

    risk_score = sum(int(item.get("risk_score", 0)) for item in state.findings)
    state.risk_score = int(risk_score)
    if state.risk_score >= 70:
        state.risk_level = "high"
    elif state.risk_score >= 30:
        state.risk_level = "medium"
    else:
        state.risk_level = "low"

    log.info("audit_completed", document_id=document_id, risk_level=state.risk_level)
    return state
