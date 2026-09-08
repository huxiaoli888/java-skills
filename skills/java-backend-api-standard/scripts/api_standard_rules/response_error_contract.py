from __future__ import annotations

import re
from pathlib import Path
from typing import Type


ERROR_CODE_PATTERN = re.compile(r"^(000000|[A-Z]{2}\d{4})$")


def _quoted_code_literals(text: str) -> list[str]:
    literals = re.findall(r'"((?=[A-Za-z0-9]*\d)[A-Za-z0-9]{5,6})"', text)
    return sorted(set(literals))


def check_api_result_contract(path: Path, text: str, finding_type: Type) -> list:
    findings: list = []
    if path.name != "ApiResult.java":
        return findings

    required_fields = ["String reqid", "String code", "String message", "long ts", "T data"]
    for field in required_fields:
        if field not in text:
            findings.append(finding_type(
                "ERROR",
                "api-result-contract",
                str(path),
                1,
                f"ApiResult should expose {field} for the standard response envelope",
            ))

    forbidden_fields = ["String msg", "String traceId", "long timestamp", "int code"]
    for field in forbidden_fields:
        if field in text:
            findings.append(finding_type(
                "ERROR",
                "api-result-contract",
                str(path),
                1,
                f"ApiResult contains legacy field {field}; use reqid/code/message/ts/data",
            ))

    if '"000000"' not in text:
        findings.append(finding_type(
            "ERROR",
            "api-result-success-code",
            str(path),
            1,
            'ApiResult success code should be the string "000000"',
        ))

    if "private ApiResult(" in text and "reqidOrEmpty" not in text and "normalizeReqid" not in text:
        findings.append(finding_type(
            "ERROR",
            "api-result-reqid-null-normalization",
            str(path),
            1,
            "ApiResult should normalize null reqid to an empty string so public JSON never returns reqid:null",
        ))

    return findings


def check_error_code_contract(path: Path, text: str, finding_type: Type) -> list:
    findings: list = []
    if path.name != "ErrorCode.java":
        return findings

    if ".common.code;" not in text:
        findings.append(finding_type(
            "ERROR",
            "error-code-package-contract",
            str(path),
            1,
            "ErrorCode should live in common.code; common.error is reserved away from the error code contract",
        ))

    if "String code()" not in text:
        findings.append(finding_type(
            "ERROR",
            "error-code-contract",
            str(path),
            1,
            "ErrorCode.code() should return String to preserve 000000 and SMEEEE codes",
        ))

    if "httpStatus" in text:
        findings.append(finding_type(
            "ERROR",
            "error-code-contract",
            str(path),
            1,
            "ErrorCode should not expose httpStatus(); handled business failures use HTTP 200 and body code",
        ))

    if "int code()" in text:
        findings.append(finding_type(
            "ERROR",
            "error-code-contract",
            str(path),
            1,
            "ErrorCode.code() still returns int; use String",
        ))

    return findings


def check_common_error_code_contract(path: Path, text: str, finding_type: Type) -> list:
    findings: list = []
    if path.name != "CommonErrorCode.java":
        return findings

    if ".common.code;" not in text:
        findings.append(finding_type(
            "ERROR",
            "error-code-package-contract",
            str(path),
            1,
            "CommonErrorCode should live in common.code; common.error is reserved away from the error code contract",
        ))

    required_codes = [
        "000000",
        "AC0001",
        "AC0002",
        "AC0003",
        "AC0004",
        "AC0005",
        "AC0006",
        "AC0007",
        "AC0008",
        "AC0009",
        "AC9999",
    ]
    for code in required_codes:
        if f'"{code}"' not in text:
            findings.append(finding_type(
                "ERROR",
                "common-error-code-contract",
                str(path),
                1,
                f"CommonErrorCode should define {code}",
            ))

    for code in _quoted_code_literals(text):
        if not ERROR_CODE_PATTERN.match(code):
            findings.append(finding_type(
                "ERROR",
                "error-code-format",
                str(path),
                1,
                f"Error code {code} should be 000000 or match two uppercase letters plus four digits, for example AC0001",
            ))

    if "int code" in text or "Integer code" in text:
        findings.append(finding_type(
            "ERROR",
            "common-error-code-contract",
            str(path),
            1,
            "CommonErrorCode should keep code as String, not numeric status/code",
        ))

    if "httpStatus" in text:
        findings.append(finding_type(
            "ERROR",
            "common-error-code-contract",
            str(path),
            1,
            "CommonErrorCode should not carry httpStatus; keep HTTP status out of business error code contract",
        ))

    return findings
