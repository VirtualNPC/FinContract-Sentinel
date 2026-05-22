from pathlib import Path
import json

import yaml

from fincontract.knowledge.retriever import KnowledgeRetriever
from fincontract.knowledge.store import KnowledgeStore
from fincontract.tools.rule_engine import RuleEngine


def _write_rules(path: Path) -> None:
    rules = [
        {
            "id": "require_basis",
            "type": "keyword",
            "keyword": "approval",
            "risk_score": 10,
            "message": "Approval clause found",
            "basis_required": True,
            "basis_refs": ["INTERNAL_CONTRACT_POLICY#approval_clause"],
        }
    ]
    path.write_text(yaml.safe_dump(rules), encoding="utf-8")


def _write_knowledge(path: Path) -> None:
    record = {
        "doc_id": "INTERNAL_CONTRACT_POLICY",
        "title": "Internal Contract Policy",
        "version": "2026-05",
        "effective_date": "2026-05-01",
        "source": "internal",
        "chunk_id": "approval_clause",
        "text": "Approval clause must be present for contracts above threshold.",
    }
    path.write_text(json.dumps(record) + "\n", encoding="utf-8")


def test_basis_missing_when_knowledge_absent(tmp_path: Path) -> None:
    rules_path = tmp_path / "rules.yaml"
    _write_rules(rules_path)

    store = KnowledgeStore(tmp_path / "knowledge")
    retriever = KnowledgeRetriever(store)
    engine = RuleEngine(rules_path=rules_path, retriever=retriever)

    results = engine.evaluate("approval required")
    assert results[0]["basis_missing"] is True


def test_basis_found_when_knowledge_present(tmp_path: Path) -> None:
    rules_path = tmp_path / "rules.yaml"
    _write_rules(rules_path)

    knowledge_dir = tmp_path / "knowledge"
    knowledge_dir.mkdir(parents=True, exist_ok=True)
    knowledge_file = knowledge_dir / "knowledge.jsonl"
    _write_knowledge(knowledge_file)

    store = KnowledgeStore(knowledge_dir)
    retriever = KnowledgeRetriever(store)
    engine = RuleEngine(rules_path=rules_path, retriever=retriever)

    results = engine.evaluate("approval required")
    assert results[0]["basis_missing"] is False
    assert results[0]["basis"][0]["doc_id"] == "INTERNAL_CONTRACT_POLICY"
