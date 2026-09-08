"""HTTP boundary security component checks."""

from __future__ import annotations

import re
from pathlib import Path

from api_standard_rules.security_contract_common import STANDARD_CONTRACT, require_terms


def check_signature_headers(path: Path, text: str, finding_factory) -> list:
    if path.name != "SignatureHeaders.java":
        return []
    findings = require_terms(
        path,
        text,
        STANDARD_CONTRACT["signatureHeaders"]["requiredConstantFragments"],
        "ERROR",
        "signature-header-contract",
        "SignatureHeaders should define ",
        finding_factory,
    )
    for header in STANDARD_CONTRACT["requestHeaders"]["obsolete"]:
        if re.search(rf'["\']{re.escape(header)}["\']', text):
            findings.append(finding_factory(
                path,
                "ERROR",
                "signature-header-contract",
                f"SignatureHeaders contains obsolete common header {header}",
            ))
    return findings


def check_access_log(path: Path, text: str, finding_factory) -> list:
    if path.name != "RequestTraceLogFilter.java":
        return []
    return require_terms(
        path,
        text,
        [
            "requestTime",
            "responseTime",
            "durationMs",
            "requestBody",
            "code",
            "message",
            "x-reqid",
            "x-udid",
            "x-api-key",
            "AccessLogContext.resultOrDefault",
            "CachedBodyHttpServletRequest",
            "RequestBodyMasker",
        ],
        "ERROR",
        "access-log-contract",
        "RequestTraceLogFilter should capture ",
        finding_factory,
    )


def check_request_body_masker(path: Path, text: str, finding_factory) -> list:
    if path.name != "RequestBodyMasker.java":
        return []
    findings = require_terms(
        path,
        text,
        ["password", "token", "secret", "captcha", "smsCode", "idCard", "bankCard"],
        "ERROR",
        "request-body-masker-contract",
        "RequestBodyMasker should mask ",
        finding_factory,
    )
    for term in ["apiKey", "udid"]:
        if f'"{term}"' in text:
            findings.append(finding_factory(
                path,
                "WARN",
                "request-body-masker-contract",
                f"RequestBodyMasker masks {term}; standard logs this caller identity field raw by default",
            ))
    return findings


def check_security_error_response(path: Path, text: str, finding_factory) -> list:
    if path.name != "SecurityErrorResponseWriter.java":
        return []
    return require_terms(
        path,
        text,
        ["reqid", "code", "message", "ts", "AccessLogContext.setResult"],
        "ERROR",
        "security-error-response-contract",
        "SecurityErrorResponseWriter should write unified field or log result: ",
        finding_factory,
    )


def check_cors_components(path: Path, text: str, finding_factory) -> list:
    if path.name == "ApiCorsConfiguration.java":
        return require_terms(
            path,
            text,
            ["WebMvcConfigurer", "addCorsMappings", "allowedOrigins", "allowedOriginPatterns", "allowCredentials", "通配 origin"],
            "ERROR",
            "cors-component-contract",
            "ApiCorsConfiguration should include ",
            finding_factory,
        )
    if path.name == "ApiCorsProperties.java":
        return require_terms(
            path,
            text,
            ["allowedOrigins", "allowedOriginPatterns", "allowedMethods", "allowedHeaders", "exposedHeaders", "allowCredentials", "maxAge"],
            "ERROR",
            "cors-component-contract",
            "ApiCorsProperties should expose ",
            finding_factory,
        )
    return []


def check_sql_injection_components(path: Path, text: str, finding_factory) -> list:
    if path.name == "SqlInjectionFilter.java":
        return require_terms(
            path,
            text,
            ["getQueryString", "isCheckFormParameters", "getParameterMap", "SecurityErrorResponseWriter", "PARAM_INVALID"],
            "ERROR",
            "sql-injection-component-contract",
            "SqlInjectionFilter should include ",
            finding_factory,
        )
    if path.name == "SqlInjectionGuard.java":
        return require_terms(
            path,
            text,
            ["Pattern.compile", "hasInjectionRisk"],
            "ERROR",
            "sql-injection-component-contract",
            "SqlInjectionGuard should include ",
            finding_factory,
        )
    if path.name == "SqlInjectionProperties.java":
        return require_terms(
            path,
            text,
            ["checkQueryParameters", "checkFormParameters", "blockedPatterns", "excludePaths"],
            "ERROR",
            "sql-injection-component-contract",
            "SqlInjectionProperties should expose ",
            finding_factory,
        )
    return []


def check_rate_limit_components(path: Path, text: str, finding_factory) -> list:
    if path.name == "RateLimitFilter.java":
        return require_terms(
            path,
            text,
            ["RateLimiter", "SecurityErrorResponseWriter", "RATE_LIMITED", "resolveIdentity", "matches"],
            "ERROR",
            "rate-limit-component-contract",
            "RateLimitFilter should include ",
            finding_factory,
        )
    if path.name == "RateLimitProperties.java":
        return require_terms(
            path,
            text,
            ["defaultPermits", "defaultWindow", "identityHeaders", "excludePaths", "rules", "pathPattern"],
            "ERROR",
            "rate-limit-component-contract",
            "RateLimitProperties should expose ",
            finding_factory,
        )
    if path.name == "InMemoryRateLimiter.java":
        return require_terms(
            path,
            text,
            ["ConcurrentHashMap", "window", "permits"],
            "WARN",
            "rate-limit-component-contract",
            "InMemoryRateLimiter should include development limiter term ",
            finding_factory,
        )
    return []


def check_file_upload_components(path: Path, text: str, finding_factory) -> list:
    if path.name == "FileUploadSecurityPolicy.java":
        return require_terms(
            path,
            text,
            ["isAllowed", "allowedExtensions", "allowedContentTypes", "maxBytes"],
            "ERROR",
            "file-upload-component-contract",
            "FileUploadSecurityPolicy should include ",
            finding_factory,
        )
    if path.name == "FileUploadSecurityProperties.java":
        return require_terms(
            path,
            text,
            ["allowedExtensions", "allowedContentTypes", "maxBytes"],
            "ERROR",
            "file-upload-component-contract",
            "FileUploadSecurityProperties should expose ",
            finding_factory,
        )
    return []


