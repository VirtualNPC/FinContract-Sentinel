from pathlib import Path
import re

import yaml

from fincontract.core.errors import RuleError


class RuleEngine:
    def __init__(self, rules_path: Path | None = None) -> None:
        default_path = Path(__file__).resolve().parents[1] / "rules" / "default_rules.yaml"
        self.rules_path = rules_path or default_path
        self.rules = self._load_rules()

    def _load_rules(self) -> list[dict]:
        try:
            raw = self.rules_path.read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            raise RuleError(f"Rules file not found: {self.rules_path}") from exc

        data = yaml.safe_load(raw)
        if not isinstance(data, list):
            raise RuleError("Rules file must contain a list of rules.")
        return data

    def evaluate(self, text: str) -> list[dict]:
        results: list[dict] = []
        for rule in self.rules:
            rule_type = rule.get("type", "")
            if rule_type == "regex":
                pattern = rule.get("pattern", "")
                match = re.search(pattern, text, flags=re.IGNORECASE)
                if match:
                    results.append(self._format_result(rule, evidence=match.group(0)))
            elif rule_type == "keyword":
                keyword = rule.get("keyword", "")
                if keyword and keyword.lower() in text.lower():
                    results.append(self._format_result(rule, evidence=keyword))
            elif rule_type == "keyword_absent":
                keyword = rule.get("keyword", "")
                if keyword and keyword.lower() not in text.lower():
                    results.append(self._format_result(rule, evidence=f"missing:{keyword}"))
        return results

    def _format_result(self, rule: dict, evidence: str | None = None) -> dict:
        return {
            "rule_id": rule.get("id", "unknown"),
            "message": rule.get("message", ""),
            "risk_score": int(rule.get("risk_score", 0)),
            "evidence": evidence,
        }
