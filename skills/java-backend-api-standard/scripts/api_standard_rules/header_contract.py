"""Shared API request-header contract checks."""

from __future__ import annotations

import re
from pathlib import Path

from api_standard_rules.security_contract_common import STANDARD_CONTRACT


def check_shared_header_contract(root: Path, profile: str, iter_project_text_files, read_text, check_allowed_headers, check_document_header, check_obsolete_header) -> list:
    findings = []
    for path in iter_project_text_files(root):
        text = read_text(path)
        findings.extend(check_allowed_headers(path, text, profile))
        findings.extend(check_document_header(path, text))
        findings.extend(check_obsolete_header(path, text))
    return findings


def check_allowed_headers_contract(path: Path, text: str, profile: str, finding_factory, line_number) -> list:
    if "allowed-headers:" not in text:
        return []
    required = list(STANDARD_CONTRACT["requestHeaders"]["common"])
    normalized = str(path).replace("\\", "/").lower()
    if profile == "standard" and ("sdk" in normalized or "openapi" in normalized):
        required.extend(STANDARD_CONTRACT["requestHeaders"]["sdkOnly"])
    missing = [header for header in required if header not in text]
    if not missing:
        return []
    return [finding_factory(path, "ERROR", "shared-header-contract", "CORS allowed-headers 缺少共享请求头：" + ", ".join(missing), line_number(text, text.find("allowed-headers:")))]


def check_document_header_contract(path: Path, text: str, finding_factory) -> list:
    if path.suffix.lower() != ".md":
        return []
    if path.name not in {"api_inventory.md", "system_architecture.md", "api-contract.md", "module-standard.md", "security.md"}:
        return []
    if not mentions_api_headers(text):
        return []
    required = STANDARD_CONTRACT["requestHeaders"]["common"]
    missing = [header for header in required if header not in text]
    if not missing:
        return []
    return [finding_factory(path, "WARN", "shared-header-contract", "请求头文档缺少共享请求头：" + ", ".join(missing), 1)]


def mentions_api_headers(text: str) -> bool:
    markers = ["请求头", "request header", "x-reqid", "x-sign", "authorization"]
    lowered = text.lower()
    return any(marker.lower() in lowered for marker in markers)


def check_obsolete_header_contract(path: Path, text: str, finding_factory, line_number) -> list:
    if not should_check_obsolete_headers(path):
        return []
    findings = []
    for header in STANDARD_CONTRACT["requestHeaders"]["obsolete"]:
        index = text.find(header)
        if index < 0:
            continue
        findings.append(finding_factory(path, "ERROR", "shared-header-contract", f"项目文档或配置包含已废弃请求头：{header}", line_number(text, index)))
    return findings


def should_check_obsolete_headers(path: Path) -> bool:
    normalized = str(path).replace("\\", "/").lower()
    if "/scripts/test_" in normalized or "\\scripts\\test_" in normalized:
        return False
    if "api-standard-contract.json" in normalized:
        return False
    return path.suffix.lower() in {".md", ".yml", ".yaml", ".properties", ".ps1", ".xml", ".txt"} or path.name == "AGENTS.md"
