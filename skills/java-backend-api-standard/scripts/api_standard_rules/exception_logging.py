from __future__ import annotations

import re
from pathlib import Path
from typing import Callable, TypeVar


FindingT = TypeVar("FindingT")
FindingFactory = Callable[[str, str, str, int, str], FindingT]
LineNumber = Callable[[str, int], int]


def check_swallowed_exception(
    path: Path,
    text: str,
    finding_factory: FindingFactory[FindingT],
    line_number: LineNumber,
) -> list[FindingT]:
    if path.suffix != ".java":
        return []

    findings: list[FindingT] = []
    catch_pattern = re.compile(r"catch\s*\((?P<declaration>[^)]*(?:Exception|Throwable)[^)]*)\)\s*\{")
    for match in catch_pattern.finditer(text):
        body_start = match.end()
        body_end = find_matching_brace(text, body_start - 1)
        if body_end <= body_start:
            continue
        body = text[body_start:body_end]
        compact = re.sub(r"/\*.*?\*/|//.*?$", "", body, flags=re.DOTALL | re.MULTILINE).strip()
        if not compact:
            findings.append(swallowed_exception_finding(path, text, match.start(), finding_factory, line_number))
            continue
        if ".error(" in body or "throw " in body or ".onError(" in body:
            continue
        if is_expected_rejection_handled(match.group("declaration"), body):
            continue
        findings.append(swallowed_exception_finding(path, text, match.start(), finding_factory, line_number))
    return findings


def is_expected_rejection_handled(declaration: str, body: str) -> bool:
    if "log.info(" not in body:
        return False
    if (
        ("SignatureAuthenticationException" in declaration or "NettyAuthenticationException" in declaration)
        and ("SecurityErrorResponseWriter.write" in body or "responseWriter.fail" in body)
    ):
        return True
    if (
        (
            "JsonProcessingException" in declaration
            or "ProtocolDecodeException" in declaration
            or "ProtocolFormatException" in declaration
            or "MessageDecodeException" in declaration
        )
        and "protocol_invalid" in body
        and "responseWriter.fail" in body
        and '"AC0001"' in body
    ):
        return True
    if "RuntimeException" in declaration and (
        "signature_timestamp_invalid" in body or "cms_signature_timestamp_invalid" in body
    ) and "return true" in body:
        return True
    return False


def check_business_exception_control_flow(
    path: Path,
    text: str,
    finding_factory: FindingFactory[FindingT],
    line_number: LineNumber,
) -> list[FindingT]:
    if path.suffix != ".java":
        return []

    normalized = str(path).replace("\\", "/").lower()
    if not any(segment in normalized for segment in ["/service/", "/domain/", "/application/"]):
        return []

    findings: list[FindingT] = []
    pattern = re.compile(r"throw\s+new\s+(?:[A-Za-z_][A-Za-z0-9_]*\.)?BusinessException\s*\(")
    for match in pattern.finditer(text):
        findings.append(finding_factory(
            "WARN",
            "business-exception-control-flow",
            str(path),
            line_number(text, match.start()),
            "normal business failure should not use BusinessException as regular control flow in service/domain/application layer",
        ))
    return findings


def find_matching_brace(text: str, open_brace_index: int) -> int:
    depth = 0
    for index in range(open_brace_index, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
    return -1


def swallowed_exception_finding(
    path: Path,
    text: str,
    index: int,
    finding_factory: FindingFactory[FindingT],
    line_number: LineNumber,
) -> FindingT:
    return finding_factory(
        "WARN",
        "exception-swallowed",
        str(path),
        line_number(text, index),
        "catch block handles exception without log.error, rethrow, or onError callback",
    )
