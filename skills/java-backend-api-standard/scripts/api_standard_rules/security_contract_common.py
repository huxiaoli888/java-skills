"""Shared helpers for Java API security component checks."""

from __future__ import annotations

import json
import re
from pathlib import Path


def load_contract() -> dict:
    contract_path = Path(__file__).resolve().parents[2] / "references" / "api-standard-contract.json"
    return json.loads(contract_path.read_text(encoding="utf-8"))


STANDARD_CONTRACT = load_contract()


def require_terms(path: Path, text: str, terms: list[str], severity: str, rule: str, message_prefix: str, finding_factory) -> list:
    findings = []
    for term in terms:
        if term not in text:
            findings.append(finding_factory(path, severity, rule, f"{message_prefix}{term}"))
    return findings

