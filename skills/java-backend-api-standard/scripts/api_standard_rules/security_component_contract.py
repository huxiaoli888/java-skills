"""Security component contract checks for java-backend-api-standard."""

from __future__ import annotations

from api_standard_rules.security_contract_common import STANDARD_CONTRACT
from api_standard_rules import security_http_components, security_signature_components


def check_security_component_contract(path, text: str, finding_factory) -> list:
    checks = [
        security_http_components.check_signature_headers,
        security_http_components.check_access_log,
        security_http_components.check_request_body_masker,
        security_http_components.check_security_error_response,
        security_http_components.check_cors_components,
        security_http_components.check_sql_injection_components,
        security_http_components.check_rate_limit_components,
        security_http_components.check_file_upload_components,
        security_signature_components.check_signature_authentication,
        security_signature_components.check_signature_canonical_payload,
        security_signature_components.check_cms_signature_filter,
        security_signature_components.check_replay_store,
        security_signature_components.check_idempotency_components,
    ]
    findings = []
    for check in checks:
        findings.extend(check(path, text, finding_factory))
    return findings
