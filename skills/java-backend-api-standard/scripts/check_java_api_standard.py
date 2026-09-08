#!/usr/bin/env python3
"""Static checks for the java-backend-api-standard skill.

The checker is intentionally heuristic. It catches obvious contract drift without
pretending to replace compilation, tests, ArchUnit, or framework-specific rules.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List

sys.dont_write_bytecode = True

from api_standard_rules import controller_contract, environment_config, exception_logging, header_contract, localization, response_error_contract, security_component_contract

for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


EXCLUDED_DIRS = {
    ".git",
    ".idea",
    ".mvn",
    "target",
    "build",
    "out",
    "node_modules",
}


@dataclass
class Finding:
    severity: str
    rule: str
    file: str
    line: int
    message: str


def localize_message(message: str) -> str:
    return localization.localize_message(message)


def localize_finding(finding: Finding) -> Finding:
    return localization.localize_finding(finding, Finding)


def iter_java_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        if path.suffix == ".java" or path.name.endswith("Mapper.xml"):
            yield path


def iter_pom_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("pom.xml"):
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        yield path


def iter_project_text_files(root: Path) -> Iterable[Path]:
    text_suffixes = {".md", ".ps1", ".yml", ".yaml", ".xml", ".properties", ".txt"}
    for path in root.rglob("*"):
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        if path.is_file() and (path.suffix.lower() in text_suffixes or path.name == "AGENTS.md"):
            yield path


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def check_swallowed_exception(path: Path, text: str) -> List[Finding]:
    return exception_logging.check_swallowed_exception(path, text, Finding, line_number)


def check_business_exception_control_flow(path: Path, text: str) -> List[Finding]:
    return exception_logging.check_business_exception_control_flow(path, text, Finding, line_number)


def is_controller(path: Path, text: str) -> bool:
    return controller_contract.is_controller(path, text)


def is_request_dto(path: Path, text: str) -> bool:
    return controller_contract.is_request_dto(path, text)


def check_required_components(root: Path, files: List[Path], profile: str = "standard") -> List[Finding]:
    names = {path.name for path in files}
    required = dict(security_component_contract.STANDARD_CONTRACT["requiredComponents"]["common"])
    if profile == "minimal":
        for name in security_component_contract.STANDARD_CONTRACT["requiredComponents"]["minimalOmit"]:
            required.pop(name, None)
    findings: List[Finding] = []
    for name, message in sorted(required.items()):
        if name not in names:
            findings.append(Finding("WARN", "required-component", str(root), 0, message))
    return [localize_finding(finding) for finding in findings]


def check_environment_configs(root: Path) -> List[Finding]:
    findings = environment_config.check_environment_configs(root, EXCLUDED_DIRS, Finding, read_text)
    return [localize_finding(finding) for finding in findings]


def find_application_file(resources_dir: Path) -> Path | None:
    return environment_config.find_application_file(resources_dir)


def check_shared_header_contract(root: Path, profile: str) -> List[Finding]:
    return header_contract.check_shared_header_contract(
        root,
        profile,
        iter_project_text_files,
        read_text,
        check_allowed_headers_contract,
        check_document_header_contract,
        check_obsolete_header_contract,
    )


def check_allowed_headers_contract(path: Path, text: str, profile: str) -> List[Finding]:
    return header_contract.check_allowed_headers_contract(path, text, profile, make_finding_at_line, line_number)


def check_document_header_contract(path: Path, text: str) -> List[Finding]:
    return header_contract.check_document_header_contract(path, text, make_finding_at_line)


def mentions_api_headers(text: str) -> bool:
    return header_contract.mentions_api_headers(text)


def check_obsolete_header_contract(path: Path, text: str) -> List[Finding]:
    return header_contract.check_obsolete_header_contract(path, text, make_finding_at_line, line_number)


def should_check_obsolete_headers(path: Path) -> bool:
    return header_contract.should_check_obsolete_headers(path)

def check_api_result_contract(path: Path, text: str) -> List[Finding]:
    return response_error_contract.check_api_result_contract(path, text, Finding)



def check_error_code_contract(path: Path, text: str) -> List[Finding]:
    return response_error_contract.check_error_code_contract(path, text, Finding)



def check_common_error_code_contract(path: Path, text: str) -> List[Finding]:
    return response_error_contract.check_common_error_code_contract(path, text, Finding)


def check_server_generated_reqid(path: Path, text: str) -> List[Finding]:
    normalized = str(path).replace("\\", "/").lower()
    if "/netty/" in normalized or path.name.startswith("Netty"):
        return []
    if "UUID.randomUUID().toString()" not in text:
        return []

    findings: List[Finding] = []
    uuid_helper_names = {
        match.group(1)
        for match in re.finditer(
            r"(?:public|private|protected)?\s*(?:static\s+)?String\s+(\w+)\s*\([^)]*\)\s*\{[^{}]*UUID\.randomUUID\(\)\.toString\(\)[^{}]*\}",
            text,
            flags=re.DOTALL,
        )
    }
    for match in re.finditer(
        r"[^;\n]*(?:requestId|reqid|request_id)[^;\n]*UUID\.randomUUID\(\)\.toString\(\)[^;]*;",
        text,
        flags=re.IGNORECASE,
    ):
        findings.append(Finding(
            "ERROR",
            "server-generated-reqid",
            str(path),
            line_number(text, match.start()),
            "HTTP 服务端不得为 x-reqid 静默生成 UUID；x-reqid 应由终端或 H5/客户端生成并原样写入响应",
        ))
    for helper_name in uuid_helper_names:
        pattern = (
            r"[^;\n]*(?:requestId|reqid|request_id)[^;\n]*getHeader\s*\([^;\n]*(?:REQUEST_ID_HEADER|[\"']x-reqid[\"'])[^;\n]*"
            + re.escape(helper_name)
            + r"\s*\([^;]*;"
        )
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            findings.append(Finding(
                "ERROR",
                "server-generated-reqid",
                str(path),
                line_number(text, match.start()),
                "HTTP 服务端不得通过 helper 为 x-reqid 静默生成 UUID；x-reqid 应由终端或 H5/客户端生成并原样写入响应",
            ))
    return findings



def make_finding(path: Path, severity: str, rule: str, message: str) -> Finding:
    return Finding(severity, rule, str(path), 1, message)


def make_finding_at_line(path: Path, severity: str, rule: str, message: str, line: int) -> Finding:
    return Finding(severity, rule, str(path), line, message)


def check_security_component_contract(path: Path, text: str) -> List[Finding]:
    return security_component_contract.check_security_component_contract(path, text, make_finding)

def check_operation_audit_contract(path: Path, text: str) -> List[Finding]:
    findings: List[Finding] = []
    if path.name == "OperationAuditAspect.java":
        required_terms = ["@Around", "OperationAuditService", "TraceContext.traceId", "TraceContext.requestId", "clientIp"]
        for term in required_terms:
            if term not in text:
                findings.append(Finding(
                    "ERROR",
                    "operation-audit-contract",
                    str(path),
                    1,
                    f"OperationAuditAspect should include {term}",
                ))
        if "Arrays.deepToString" in text or "joinPoint.getArgs()" in text:
            findings.append(Finding(
                "WARN",
                "operation-audit-contract",
                str(path),
                1,
                "OperationAuditAspect should not log raw method arguments by default",
            ))
    if path.name == "OperationAuditRecord.java":
        required_terms = ["operator", "operationType", "businessId", "success", "traceId", "reqid", "durationMs"]
        for term in required_terms:
            if term not in text:
                findings.append(Finding(
                    "ERROR",
                    "operation-audit-record-contract",
                    str(path),
                    1,
                    f"OperationAuditRecord should include {term}",
                ))
    return findings


def check_admin_api_key_usage(path: Path, text: str) -> List[Finding]:
    normalized = str(path).replace("\\", "/").lower()
    if "cms" not in normalized and "admin" not in normalized:
        return []
    if "x-api-key" not in text and "SignatureHeaders.API_KEY" not in text:
        return []
    if ("/client/" in normalized or "\\client\\" in normalized) and (
        "RestClient" in text or "WebClient" in text or "RestTemplate" in text
    ):
        return []
    return [Finding(
        "ERROR",
        "admin-api-key-forbidden",
        str(path),
        1,
        "admin/CMS API should not use x-api-key as a common request parameter",
    )]


def check_security_exclude_contract(path: Path, text: str) -> List[Finding]:
    if not is_security_exclude_candidate(path):
        return []

    findings: List[Finding] = []
    findings.extend(check_security_exclude_properties(path, text))
    findings.extend(check_security_filter_order(path, text))
    return findings


def is_security_exclude_candidate(path: Path) -> bool:
    normalized = str(path).replace("\\", "/").lower()
    if not (path.name.endswith("SecurityProperties.java") or path.name.endswith("SecurityFilter.java")):
        return False
    return "cms" in normalized or "sdk" in normalized or "admin" in normalized


def check_security_exclude_properties(path: Path, text: str) -> List[Finding]:
    findings: List[Finding] = []
    if "udidExcludePaths" not in text and "getUdidExcludePaths" not in text and "udid-exclude-paths" not in text:
        findings.append(Finding(
            "WARN",
            "udid-exclude-paths-missing",
            str(path),
            1,
            "security configuration should expose udid-exclude-paths for login/captcha/health endpoints",
        ))
    if "authExcludePaths" not in text and "getAuthExcludePaths" not in text and "auth-exclude-paths" not in text:
        findings.append(Finding(
            "WARN",
            "auth-exclude-paths-missing",
            str(path),
            1,
            "security configuration should distinguish auth-exclude-paths from udid-exclude-paths",
        ))
    return findings


def check_security_filter_order(path: Path, text: str) -> List[Finding]:
    findings: List[Finding] = []
    auth_check_index = text.find("isAuthExcluded")
    udid_check_index = text.find("isUdidExcluded")
    authentication_index = min(
        [index for index in [
            text.find("signatureAuthenticationSupport.authenticate"),
            text.find("isBearerToken"),
        ] if index >= 0],
        default=-1,
    )
    if auth_check_index >= 0 and udid_check_index >= 0 and auth_check_index > udid_check_index:
        findings.append(Finding(
            "ERROR",
            "security-filter-order",
            str(path),
            line_number(text, udid_check_index),
            "security filter should evaluate auth-exclude-paths before udid-exclude-paths",
        ))
    if udid_check_index >= 0 and authentication_index >= 0 and udid_check_index > authentication_index:
        findings.append(Finding(
            "ERROR",
            "security-filter-order",
            str(path),
            line_number(text, authentication_index),
            "security filter should check x-udid before token or signature authentication unless auth-exclude-paths matched",
        ))
    return findings


def check_module_security_components(root: Path, files: List[Path], profile: str = "standard") -> List[Finding]:
    findings: List[Finding] = []
    names = {path.name for path in files}
    normalized_paths = [str(path).replace("\\", "/").lower() for path in files]
    has_cms = any("/cms/" in path or "-cms-api/" in path or "/admin/" in path for path in normalized_paths)
    has_sdk = any("/sdk/" in path or "-sdk-api/" in path for path in normalized_paths)

    if has_cms:
        for name in ["CmsSecurityFilter.java", "CmsSecurityProperties.java", "CmsSecurityConfiguration.java", "AdminPrincipal.java"]:
            if name not in names:
                findings.append(Finding("WARN", "cms-security-component-missing", str(root), 0, f"CMS 模块存在，但未找到安全组件 {name}"))
    if has_sdk:
        for name in ["SdkSecurityFilter.java", "SdkSecurityProperties.java", "SdkSecurityConfiguration.java"]:
            if name not in names:
                findings.append(Finding("WARN", "sdk-security-component-missing", str(root), 0, f"SDK 模块存在，但未找到安全组件 {name}"))
        for name in ["ApiCredential.java", "ApiCredentialResolver.java", "SignatureAuthenticationSupport.java", "AuthenticatedSignatureRequest.java"]:
            if name not in names:
                findings.append(Finding("WARN", "sdk-security-component-missing", str(root), 0, f"SDK 模块存在，但未找到通用签名组件 {name}"))
    elif profile != "minimal":
        findings.append(Finding("WARN", "sdk-module-missing", str(root), 0, "standard profile 应包含 SDK API 模块；如需单 CMS 项目，请使用 --profile minimal"))
    return findings


def check_netty_module_contract(root: Path, files: List[Path]) -> List[Finding]:
    findings: List[Finding] = []
    netty_modules = [
        path for path in root.iterdir()
        if path.is_dir() and path.name.lower().endswith("-netty")
    ]
    if not netty_modules:
        return findings

    names = {path.name for path in files}
    required_java_files = {
        "NettyMessageEnvelope.java": "Netty 模块缺少统一请求 envelope",
        "NettyResponseWriter.java": "Netty 模块缺少统一响应/ACK 写入器",
        "NettyMessageDispatcher.java": "Netty 模块缺少 func + version handler dispatcher",
        "NettyMessageHandler.java": "Netty 模块缺少 handler 接口",
        "AuthMessageHandler.java": "Netty 模块缺少 AUTH handler",
        "HeartbeatMessageHandler.java": "Netty 模块缺少 HEARTBEAT handler",
        "NettyAuthenticationService.java": "Netty 模块缺少鉴权防篡改入口",
        "NettyTcpServer.java": "Netty 模块缺少 TCP 入口",
        "NettyUdpServer.java": "Netty 模块缺少 UDP 入口",
    }
    for name, message in sorted(required_java_files.items()):
        if name not in names:
            findings.append(Finding("WARN", "netty-module-component-missing", str(root), 0, message))

    for module in netty_modules:
        resources_dir = module / "src/main/resources"
        application_file = find_application_file(resources_dir)
        if application_file is None:
            findings.append(Finding("WARN", "netty-module-config-missing", str(module), 0, "Netty 模块缺少 application.yml"))
            continue
        text = read_text(application_file)
        required_terms = [
            "chaken:",
            "netty:",
            "tcp:",
            "udp:",
            "auth-timeout-ms",
            "reader-idle-seconds",
            "max-frame-bytes",
            "max-datagram-bytes",
            "route-ttl-seconds",
            "rate-limit:",
            "security:",
            "replay-ttl-seconds",
        ]
        for term in required_terms:
            if term not in text:
                findings.append(Finding(
                    "WARN",
                    "netty-module-config-missing",
                    str(application_file),
                    1,
                    f"Netty 模块配置缺少 {term}",
                ))
    return findings


def check_profile_contract(root: Path, profile: str) -> List[Finding]:
    findings: List[Finding] = []
    if profile != "minimal":
        return findings

    sdk_module_dirs = [
        path for path in root.iterdir()
        if path.is_dir() and path.name.lower().endswith("-sdk-api")
    ]
    for path in sdk_module_dirs:
        findings.append(Finding(
            "ERROR",
            "minimal-sdk-module-present",
            str(path),
            0,
            "minimal profile 不应包含 sdk-api 模块",
        ))

    strong_sdk_markers = ["sdk-api", "dev-sdk-", "test-sdk-", "$SdkModuleName", "SdkModuleName"]
    for path in iter_project_text_files(root):
        relative = str(path.relative_to(root)).replace("\\", "/")
        if "/src/main/java/" in relative or "/src/test/java/" in relative:
            continue
        text = read_text(path)
        for marker in strong_sdk_markers:
            index = text.find(marker)
            if index >= 0:
                findings.append(Finding(
                    "ERROR",
                    "minimal-sdk-contract-residue",
                    str(path),
                    line_number(text, index),
                    f"minimal profile 文档或脚本仍残留 SDK 契约标记 {marker}",
                ))
                break
    return findings


def check_controller_returns(path: Path, text: str) -> List[Finding]:
    return controller_contract.check_controller_returns(path, text, Finding, line_number)


def check_controller_unified_response(path: Path, text: str) -> List[Finding]:
    return controller_contract.check_controller_unified_response(path, text, Finding)


def check_controller_raw_returns(path: Path, text: str) -> List[Finding]:
    return controller_contract.check_controller_raw_returns(path, text, Finding, line_number)


def raw_return_finding(path: Path, text: str, index: int) -> Finding:
    return controller_contract.raw_return_finding(path, text, index, Finding, line_number)


def check_controller_entity_imports(path: Path, text: str) -> List[Finding]:
    return controller_contract.check_controller_entity_imports(path, text, Finding)


def check_validation_messages(path: Path, text: str) -> List[Finding]:
    return controller_contract.check_validation_messages(path, text, Finding, line_number)


def check_layer_dependencies(path: Path, text: str) -> List[Finding]:
    normalized = str(path).replace("\\", "/").lower()
    findings: List[Finding] = []

    forbidden = []
    if "/repository/" in normalized or "/mapper/" in normalized:
        forbidden.append((r"import\s+[\w.]+\.controller\.", "repository/mapper must not depend on controller"))
    if "/entity/" in normalized:
        forbidden.extend([
            (r"import\s+[\w.]+\.controller\.", "entity must not depend on controller"),
            (r"import\s+[\w.]+\.service\.", "entity must not depend on service"),
        ])
    if "/common/" in normalized:
        forbidden.append((r"import\s+[\w.]+\.modules\.", "common must not depend on business modules"))
    if "/dto/" in normalized:
        forbidden.append((r"import\s+[\w.]+\.service\.", "DTO must not depend on service"))

    for pattern, message in forbidden:
        for match in re.finditer(pattern, text):
            findings.append(Finding(
                "ERROR",
                "layer-dependency",
                str(path),
                line_number(text, match.start()),
                message,
            ))
    return findings


def check_sql_injection_risk(path: Path, text: str) -> List[Finding]:
    normalized = str(path).replace("\\", "/").lower()
    if "/mapper/" not in normalized and "/repository/" not in normalized and not path.name.endswith("Mapper.xml"):
        return []
    if "${" not in text:
        return []
    return [Finding(
        "WARN",
        "sql-injection-risk",
        str(path),
        1,
        "mapper/repository contains ${}; use parameter binding or a server-side allowlist for dynamic fields",
    )]


def check_complex_sql_location(path: Path, text: str) -> List[Finding]:
    normalized = str(path).replace("\\", "/").lower()
    if "/mapper/" not in normalized or not path.name.endswith(".java"):
        return []

    findings: List[Finding] = []
    annotation_pattern = re.compile(r"@(Select|Update|Delete|Insert)\s*\((.*?)\)", re.DOTALL)
    complex_markers = [" join ", " group by ", " union ", " having ", "<script>", " foreach ", " case when "]
    for match in annotation_pattern.finditer(text):
        sql = re.sub(r"\s+", " ", match.group(2).lower())
        if len(sql) > 240 or any(marker in sql for marker in complex_markers):
            findings.append(Finding(
                "WARN",
                "complex-sql-should-use-xml",
                str(path),
                line_number(text, match.start()),
                "复杂 SQL 应参考 renren 项目放到 Mapper XML 中实现，不要堆在 Mapper 注解或 Java 字符串里",
            ))
    return findings


def check_persistence_contract(path: Path, text: str) -> List[Finding]:
    if path.name == "MybatisPlusConfiguration.java" and "MybatisPlusInterceptor" in text and "OptimisticLockerInnerInterceptor" not in text:
        return [Finding(
            "ERROR",
            "persistence-component-contract",
            str(path),
            1,
            "MyBatis-Plus 配置必须启用 OptimisticLockerInnerInterceptor，否则 @Version 乐观锁更新会缺少原版本参数",
        )]
    if path.name not in {"BaseEntity.java", "EntityAuditFillSupport.java"}:
        return []
    if path.name == "EntityAuditFillSupport.java":
        findings: List[Finding] = []
        if "SnowflakeIdGenerator" in text:
            findings.append(Finding(
                "ERROR",
                "persistence-component-contract",
                str(path),
                1,
                "EntityAuditFillSupport should not depend on SnowflakeIdGenerator; entity ids are generated by MyBatis-Plus ASSIGN_ID",
            ))
        if "setId(" in text:
            findings.append(Finding(
                "ERROR",
                "persistence-component-contract",
                str(path),
                1,
                "EntityAuditFillSupport should not call setId; it should only fill audit fields",
            ))
        return findings
    required_terms = [
        "@TableId(type = IdType.ASSIGN_ID)",
        "@TableField(fill = FieldFill.INSERT)",
        "@TableField(fill = FieldFill.INSERT_UPDATE)",
        "@Version",
        "@TableLogic",
        "deleted",
        "private Long version",
    ]
    findings: List[Finding] = []
    for term in required_terms:
        if term not in text:
            findings.append(Finding(
                "ERROR",
                "persistence-component-contract",
                str(path),
                1,
                f"BaseEntity should include {term}",
            ))
    if "op_version" in text or re.search(r"\bprivate\s+Long\s+opVersion\s*;", text):
        findings.append(Finding(
            "ERROR",
            "persistence-component-contract",
            str(path),
            line_number(text, text.find("op_version") if "op_version" in text else text.find("private Long opVersion")),
            "BaseEntity 乐观锁字段应使用数据库列 version 和 Java 属性 version，不应使用 op_version/opVersion",
        ))
    return findings


def check_lombok_sensitive_tostring(path: Path, text: str) -> List[Finding]:
    if "@Data" not in text and "@ToString" not in text:
        return []
    sensitive_terms = ["token", "secret", "password", "authorization", "signature", "sign"]
    lower_text = text.lower()
    if not any(term in lower_text for term in sensitive_terms):
        return []
    annotation = "@Data" if "@Data" in text else "@ToString"
    return [Finding(
        "WARN",
        "lombok-sensitive-tostring",
        str(path),
        1,
        f"sensitive DTO/entity should not use {annotation}; prefer @Getter/@Setter and explicit masking",
    )]


def check_maven_module_boundaries(root: Path) -> List[Finding]:
    findings: List[Finding] = []
    for pom in iter_pom_files(root):
        text = read_text(pom)
        normalized = str(pom.parent).replace("\\", "/").lower()
        artifact_match = re.search(r"<artifactId>\s*([^<]+)\s*</artifactId>", text)
        artifact = artifact_match.group(1) if artifact_match else pom.parent.name
        dependency_artifacts = re.findall(
            r"<dependency>.*?<artifactId>\s*([^<]+)\s*</artifactId>.*?</dependency>",
            text,
            flags=re.DOTALL,
        )
        for dependency in dependency_artifacts:
            dep = dependency.lower()
            if "common" in artifact.lower() and (dep.endswith("-cms-api") or dep.endswith("-sdk-api")):
                findings.append(Finding(
                    "ERROR",
                    "maven-module-boundary",
                    str(pom),
                    1,
                    "common 模块不得依赖 cms-api 或 sdk-api 模块",
                ))
            if ("cms-api" in normalized or artifact.lower().endswith("-cms-api")) and dep.endswith("-sdk-api"):
                findings.append(Finding(
                    "ERROR",
                    "maven-module-boundary",
                    str(pom),
                    1,
                    "cms-api 模块不得依赖 sdk-api 模块",
                ))
            if ("sdk-api" in normalized or artifact.lower().endswith("-sdk-api")) and dep.endswith("-cms-api"):
                findings.append(Finding(
                    "ERROR",
                    "maven-module-boundary",
                    str(pom),
                    1,
                    "sdk-api 模块不得依赖 cms-api 模块",
                ))
    return findings


def check_security_surface(root: Path, files: List[Path]) -> List[Finding]:
    names = {path.name for path in files}
    findings: List[Finding] = []
    high_risk_markers = ["OrderController.java", "PaymentController.java", "PaymentCallbackController.java", "RefundController.java"]
    has_high_risk = any(name in names for name in high_risk_markers)
    if not has_high_risk:
        return findings

    if "IdempotencyService.java" not in names:
        findings.append(Finding("WARN", "idempotency-missing", str(root), 0, "high-risk transaction API exists but business idempotency service was not found"))
    if "ReplayRequestStore.java" not in names:
        findings.append(Finding("WARN", "replay-protection-missing", str(root), 0, "high-risk transaction API exists but replay request store was not found"))
    if "RequestSigner.java" not in names and "SignatureVerifier.java" not in names:
        findings.append(Finding("WARN", "signature-missing", str(root), 0, "high-risk transaction API exists but signature verification utility was not found"))
    return findings


def run(root: Path, profile: str = "standard") -> List[Finding]:
    files = list(iter_java_files(root))
    findings: List[Finding] = []
    profile_findings = check_profile_contract(root, profile)
    findings.extend(profile_findings)
    findings.extend(check_required_components(root, files, profile))
    findings.extend(check_environment_configs(root))
    findings.extend(check_shared_header_contract(root, profile))
    findings.extend(check_security_surface(root, files))
    findings.extend(check_module_security_components(root, files, profile))
    findings.extend(check_netty_module_contract(root, files))
    findings.extend(check_maven_module_boundaries(root))

    for path in files:
        text = read_text(path)
        findings.extend(check_api_result_contract(path, text))
        findings.extend(check_error_code_contract(path, text))
        findings.extend(check_common_error_code_contract(path, text))
        findings.extend(check_server_generated_reqid(path, text))
        findings.extend(check_security_component_contract(path, text))
        findings.extend(check_operation_audit_contract(path, text))
        findings.extend(check_admin_api_key_usage(path, text))
        findings.extend(check_security_exclude_contract(path, text))
        findings.extend(check_controller_returns(path, text))
        findings.extend(check_validation_messages(path, text))
        findings.extend(check_layer_dependencies(path, text))
        findings.extend(check_sql_injection_risk(path, text))
        findings.extend(check_complex_sql_location(path, text))
        findings.extend(check_swallowed_exception(path, text))
        findings.extend(check_business_exception_control_flow(path, text))
        findings.extend(check_persistence_contract(path, text))
        findings.extend(check_lombok_sensitive_tostring(path, text))

    return [localize_finding(finding) for finding in findings]


def print_text(findings: List[Finding]) -> None:
    if not findings:
        print("通过：未发现明显的 java-backend-api-standard 违规项")
        return

    for finding in findings:
        finding = localize_finding(finding)
        location = finding.file
        if finding.line:
            location = f"{location}:{finding.line}"
        print(f"{finding.severity} [{finding.rule}] {location} - {finding.message}")

    errors = sum(1 for finding in findings if finding.severity == "ERROR")
    warnings = sum(1 for finding in findings if finding.severity == "WARN")
    print(f"汇总：{errors} 个错误，{warnings} 个警告")


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="检查 Java 后端 API 标准符合性。")
    parser.add_argument("project_root", help="要扫描的 Java 项目根目录")
    parser.add_argument("--profile", choices=["minimal", "standard"], default="standard", help="按生成器 profile 调整检查规则，默认 standard")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出检查结果")
    parser.add_argument("--fail-on-error", action="store_true", help="存在 ERROR 级别问题时以非 0 状态退出")
    args = parser.parse_args(argv)

    root = Path(args.project_root).resolve()
    if not root.exists():
        print(f"项目根目录不存在：{root}", file=sys.stderr)
        return 2

    findings = run(root, args.profile)
    if args.json:
        print(json.dumps([asdict(localize_finding(finding)) for finding in findings], ensure_ascii=False, indent=2))
    else:
        print_text(findings)

    if args.fail_on_error and any(finding.severity == "ERROR" for finding in findings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
