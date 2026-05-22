from uuid import uuid4

import structlog

from fincontract.agent.state import AuditState
from pathlib import Path

from fincontract.core.config import settings
from fincontract.core.errors import ParseError
from fincontract.knowledge.retriever import KnowledgeRetriever
from fincontract.knowledge.store import KnowledgeStore
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
    store = KnowledgeStore(Path(settings.knowledge_dir))
    retriever = KnowledgeRetriever(store)
    rule_engine = RuleEngine(retriever=retriever)
    state.findings = rule_engine.evaluate(text)

    needs_human_review = any(item.get("basis_missing") for item in state.findings)
    state.needs_human_review = needs_human_review

    risk_score = sum(int(item.get("risk_score", 0)) for item in state.findings)
    state.risk_score = int(risk_score)
    if state.risk_score >= 70:
        state.risk_level = "high"
    elif state.risk_score >= 30:
        state.risk_level = "medium"
    else:
        state.risk_level = "low"

    if state.risk_level == "high":
        state.overall_result = "不通过"
    elif state.risk_level == "medium" or needs_human_review:
        state.overall_result = "有条件通过"
    else:
        state.overall_result = "通过"

    if needs_human_review or state.risk_level in {"medium", "high"}:
        state.next_step = "manual_review"
    else:
        state.next_step = "auto_approve"

    state.summary = f"risk={state.risk_level}, findings={len(state.findings)}"

    log.info(
        "audit_completed",
        document_id=document_id,
        risk_level=state.risk_level,
        needs_human_review=needs_human_review,
    )
    return state
