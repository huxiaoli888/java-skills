from __future__ import annotations

import re
from pathlib import Path
from typing import Callable, Type


def is_controller(path: Path, text: str) -> bool:
    return (
        path.name.endswith("Controller.java")
        or "@RestController" in text
        or "@Controller" in text
    )


def is_request_dto(path: Path, text: str) -> bool:
    lower_parts = [part.lower() for part in path.parts]
    return (
        "request" in lower_parts
        or path.name.endswith("Request.java")
        or path.name.endswith("Query.java")
        or "class " in text
        and re.search(r"class\s+\w+(Request|Query)\b", text) is not None
    )


def check_controller_returns(
    path: Path,
    text: str,
    finding_type: Type,
    line_number: Callable[[str, int], int],
) -> list:
    findings: list = []
    if not is_controller(path, text):
        return findings

    findings.extend(check_controller_unified_response(path, text, finding_type))
    findings.extend(check_controller_raw_returns(path, text, finding_type, line_number))
    findings.extend(check_controller_entity_imports(path, text, finding_type))

    return findings


def check_controller_unified_response(path: Path, text: str, finding_type: Type) -> list:
    if "ApiResult" in text or "ResponseEntity<ApiResult" in text:
        return []
    return [finding_type(
        "ERROR",
        "controller-unified-response",
        str(path),
        1,
        "controller does not appear to return ApiResult<T>",
    )]


def check_controller_raw_returns(
    path: Path,
    text: str,
    finding_type: Type,
    line_number: Callable[[str, int], int],
) -> list:
    findings: list = []
    raw_patterns = [
        r"public\s+Map\s*<",
        r"public\s+HashMap\s*<",
        r"public\s+Object\s+",
        r"public\s+String\s+",
    ]
    for pattern in raw_patterns:
        for match in re.finditer(pattern, text):
            findings.append(raw_return_finding(path, text, match.start(), finding_type, line_number))

    for match in re.finditer(r"ResponseEntity\s*<\s*([^>]+)>", text):
        response_type = re.sub(r"\s+", "", match.group(1))
        if response_type in {"ApiResult", "byte[]"} or response_type.startswith("ApiResult<"):
            continue
        findings.append(raw_return_finding(path, text, match.start(), finding_type, line_number))
    return findings


def raw_return_finding(
    path: Path,
    text: str,
    index: int,
    finding_type: Type,
    line_number: Callable[[str, int], int],
):
    return finding_type(
        "WARN",
        "controller-raw-return",
        str(path),
        line_number(text, index),
        "controller may return a raw or non-standard response type",
    )


def check_controller_entity_imports(path: Path, text: str, finding_type: Type) -> list:
    if not re.search(r"import\s+[\w.]+\.entity\.", text):
        return []
    return [finding_type(
        "ERROR",
        "controller-entity-import",
        str(path),
        1,
        "controller imports entity package; use request/response DTOs instead",
    )]


def check_validation_messages(
    path: Path,
    text: str,
    finding_type: Type,
    line_number: Callable[[str, int], int],
) -> list:
    findings: list = []
    if not is_request_dto(path, text):
        return findings

    validation_annotation = re.compile(
        r"@(NotBlank|NotNull|NotEmpty|Size|Length|Pattern|Min|Max|DecimalMin|DecimalMax|Email)\b[^\n]*message\s*=\s*\"([^\"]*)\""
    )
    for match in validation_annotation.finditer(text):
        message = match.group(2)
        if not (message.startswith("{") and message.endswith("}")):
            findings.append(finding_type(
                "WARN",
                "validation-i18n-message",
                str(path),
                line_number(text, match.start()),
                "validation message should use an i18n key like {module.field.rule}",
            ))
    return findings
