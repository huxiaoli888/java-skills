"""Signature, replay, and idempotency component checks."""

from __future__ import annotations

from pathlib import Path

from api_standard_rules.security_contract_common import require_terms


def check_signature_authentication(path: Path, text: str, finding_factory) -> list:
    if path.name != "SignatureAuthenticationSupport.java":
        return []
    findings = require_terms(
        path,
        text,
        [
            "SignatureHeaders.SIGN",
            "SignatureHeaders.REQID",
            "SignatureHeaders.SIGNATURE_ALG",
            "SignatureHeaders.API_VERSION",
            "RequestSigner.hmacSha256Base64",
            "RequestSigner.constantTimeEquals",
            "SignatureCanonicalPayload.query",
            "SignatureCanonicalPayload.body",
            "ReplayRequestStore",
        ],
        "ERROR",
        "signature-x-sign-contract",
        "SignatureAuthenticationSupport should validate x-sign contract term ",
        finding_factory,
    )
    if "parseAuthorization" in text or "authorization: Signature" in text:
        findings.append(finding_factory(
            path,
            "ERROR",
            "signature-x-sign-contract",
            "SignatureAuthenticationSupport should read signature from x-sign; authorization is reserved for login token",
        ))
    if "getHeader(SignatureHeaders.SIGNATURE_ALG)" not in text or "getHeader(SignatureHeaders.API_VERSION)" not in text:
        findings.append(finding_factory(
            path,
            "ERROR",
            "signature-x-sign-contract",
            "SignatureAuthenticationSupport should read x-sign-alg and x-api-version",
        ))
    return findings


def check_signature_canonical_payload(path: Path, text: str, finding_factory) -> list:
    if path.name != "SignatureCanonicalPayload.java":
        return []
    return require_terms(
        path,
        text,
        [
            "canonicalUrlEncoded",
            "getQueryString",
            "rawBody",
            "return rawBody == null ? new byte[0] : rawBody",
            "URLDecoder.decode",
        ],
        "ERROR",
        "signature-payload-contract",
        "SignatureCanonicalPayload should define ",
        finding_factory,
    )


def check_cms_signature_filter(path: Path, text: str, finding_factory) -> list:
    if path.name != "CmsSecurityFilter.java":
        return []
    return require_terms(
        path,
        text,
        [
            "SignatureCanonicalPayload.query",
            "SignatureCanonicalPayload.body",
            "SignatureCanonicalPayload.body(request, wrappedRequest.getCachedBody())",
            "SignatureHeaders.SIGNATURE_ALG",
            "SignatureHeaders.API_VERSION",
        ],
        "ERROR",
        "cms-signature-payload-contract",
        "CmsSecurityFilter should validate CMS signature payload term ",
        finding_factory,
    )


def check_replay_store(path: Path, text: str, finding_factory) -> list:
    if path.name != "ReplayRequestStore.java":
        return []
    findings = []
    if "String replaySubject" not in text:
        findings.append(finding_factory(
            path,
            "ERROR",
            "replay-component-contract",
            "ReplayRequestStore should use replaySubject so CMS and SDK can share replay protection",
        ))
    if "String reqid" not in text:
        findings.append(finding_factory(
            path,
            "ERROR",
            "replay-component-contract",
            "ReplayRequestStore should use reqid to match x-reqid",
        ))
    if "String appId" in text or "String apiKey" in text:
        findings.append(finding_factory(
            path,
            "ERROR",
            "replay-component-contract",
            "ReplayRequestStore still uses appId/apiKey; use replaySubject",
        ))
    return findings


def check_idempotency_components(path: Path, text: str, finding_factory) -> list:
    if path.name == "IdempotencyService.java":
        findings = require_terms(
            path,
            text,
            ["requestFingerprint", "businessType", "businessKey"],
            "ERROR",
            "idempotency-component-contract",
            "IdempotencyService should include ",
            finding_factory,
        )
        if "String idempotencyKey" in text or "businessIdempotencyKey" in text or "requestHash" in text:
            findings.append(finding_factory(
                path,
                "ERROR",
                "idempotency-component-contract",
                "IdempotencyService should use businessType/businessKey from the business request instead of generic idempotencyKey naming",
            ))
        return findings
    if path.name == "IdempotencyRecord.java":
        findings = require_terms(
            path,
            text,
            [
                "ownerId",
                "requestFingerprint",
                "businessType",
                "businessKey",
                "IdempotencyStatus status",
                "responseSnapshot",
                "createdTime",
                "expireTime",
            ],
            "ERROR",
            "idempotency-record-contract",
            "IdempotencyRecord should include ",
            finding_factory,
        )
        if "idempotencyKey" in text or "businessIdempotencyKey" in text:
            findings.append(finding_factory(
                path,
                "ERROR",
                "idempotency-record-contract",
                "IdempotencyRecord should store the extracted businessKey, not a generic idempotencyKey field",
            ))
        return findings
    return []
