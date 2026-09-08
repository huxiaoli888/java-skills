from __future__ import annotations

import re
from pathlib import Path
from typing import Callable, TypeVar


FindingT = TypeVar("FindingT")
FindingFactory = Callable[[str, str, str, int, str], FindingT]
ReadText = Callable[[Path], str]


def check_environment_configs(
    root: Path,
    excluded_dirs: set[str],
    finding_factory: FindingFactory[FindingT],
    read_text: ReadText,
) -> list[FindingT]:
    findings: list[FindingT] = []

    for resources_dir in root.rglob("src/main/resources"):
        if not is_deployable_resources_dir(resources_dir, excluded_dirs):
            continue
        findings.extend(check_profile_files(resources_dir, finding_factory))
        findings.extend(check_application_feature_config(resources_dir, finding_factory, read_text))

    findings.extend(check_configuration_guide(root, finding_factory))
    findings.extend(check_production_configs(root, excluded_dirs, finding_factory, read_text))
    return findings


def is_deployable_resources_dir(resources_dir: Path, excluded_dirs: set[str]) -> bool:
    if any(part in excluded_dirs for part in resources_dir.parts):
        return False
    if not resources_dir.is_dir():
        return False
    return find_application_file(resources_dir) is not None


def find_application_file(resources_dir: Path) -> Path | None:
    for name in ("application.yml", "application.yaml"):
        candidate = resources_dir / name
        if candidate.exists():
            return candidate
    return None


def check_profile_files(resources_dir: Path, finding_factory: FindingFactory[FindingT]) -> list[FindingT]:
    findings: list[FindingT] = []
    for profile_file in ["application-dev.yml", "application-test.yml", "application-prod.yml"]:
        if (resources_dir / profile_file).exists():
            continue
        findings.append(finding_factory(
            "WARN",
            "environment-config-missing",
            str(resources_dir),
            0,
            f"deployable module should include {profile_file}",
        ))
    return findings


def check_application_feature_config(
    resources_dir: Path,
    finding_factory: FindingFactory[FindingT],
    read_text: ReadText,
) -> list[FindingT]:
    application_file = find_application_file(resources_dir)
    if application_file is None:
        return []
    application_text = read_text(application_file)
    netty_module = is_netty_resources_dir(resources_dir)
    checks = [
        ("rate-limit", "rate-limit-config-missing", "deployable module should configure rate limiting"),
        ("management:", "observability-config-missing", "deployable module should configure Actuator/health exposure"),
    ]
    if not netty_module:
        checks.append(("file-upload", "file-upload-config-missing", "deployable module should configure file upload security"))
    return [
        finding_factory("WARN", rule, str(application_file), 1, message)
        for key, rule, message in checks
        if key not in application_text
    ]


def is_netty_resources_dir(resources_dir: Path) -> bool:
    return any(part.endswith("-netty") for part in resources_dir.parts)


def check_configuration_guide(root: Path, finding_factory: FindingFactory[FindingT]) -> list[FindingT]:
    docs_dir = root / "docs" / "development"
    if not docs_dir.exists() or (docs_dir / "configuration_guide.md").exists():
        return []
    return [finding_factory(
        "WARN",
        "configuration-guide-missing",
        str(docs_dir),
        0,
        "project should document environment configuration in docs/development/configuration_guide.md",
    )]


def check_production_configs(
    root: Path,
    excluded_dirs: set[str],
    finding_factory: FindingFactory[FindingT],
    read_text: ReadText,
) -> list[FindingT]:
    findings: list[FindingT] = []
    for prod_file in list(root.rglob("application-prod.yml")) + list(root.rglob("application-prod.yaml")):
        if any(part in excluded_dirs for part in prod_file.parts):
            continue
        text = read_text(prod_file)
        findings.extend(check_production_placeholder_values(prod_file, text, finding_factory))
        findings.extend(check_production_secret_sources(prod_file, text, finding_factory))
        findings.extend(check_production_cors(prod_file, text, finding_factory))
        findings.extend(check_production_actuator(prod_file, text, finding_factory))
    return findings


def check_production_placeholder_values(
    prod_file: Path,
    text: str,
    finding_factory: FindingFactory[FindingT],
) -> list[FindingT]:
    forbidden_values = [
        "change-me",
        "dev-cms-token",
        "test-cms-token",
        "dev-sdk-api-key",
        "test-sdk-api-key",
        "dev-sdk-secret",
        "test-sdk-secret",
        "test-api-key",
    ]
    findings: list[FindingT] = []
    for value in forbidden_values:
        if value in text:
            findings.append(finding_factory(
                "ERROR",
                "production-config-placeholder",
                str(prod_file),
                1,
                f"production config contains development/test placeholder value {value}",
            ))
    return findings


def check_production_secret_sources(
    prod_file: Path,
    text: str,
    finding_factory: FindingFactory[FindingT],
) -> list[FindingT]:
    findings: list[FindingT] = []
    for line_index, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not is_secret_source_line(stripped):
            continue
        value = stripped.split(":", 1)[1].strip()
        if value and not value.startswith("${"):
            findings.append(finding_factory(
                "ERROR",
                "production-config-secret-source",
                str(prod_file),
                line_index,
                "production secrets should come from environment variables, configuration center, or secret manager placeholders",
            ))
    return findings


def is_secret_source_line(stripped: str) -> bool:
    return (
        stripped.startswith("default-token:")
        or stripped.startswith("default-api-key:")
        or stripped.startswith("default-secret:")
    )


def check_production_cors(
    prod_file: Path,
    text: str,
    finding_factory: FindingFactory[FindingT],
) -> list[FindingT]:
    if "allow-credentials: true" not in text or not re.search(r"(?m)^\s*-\s*['\"]?\*['\"]?\s*$", text):
        return []
    return [finding_factory(
        "ERROR",
        "production-cors-wildcard",
        str(prod_file),
        1,
        "生产环境允许凭据时，CORS 不得使用通配 origin",
    )]


def check_production_actuator(
    prod_file: Path,
    text: str,
    finding_factory: FindingFactory[FindingT],
) -> list[FindingT]:
    if not re.search(r"(?m)^\s*include:\s*['\"]?\*['\"]?\s*$", text):
        return []
    return [finding_factory(
        "ERROR",
        "production-actuator-exposure",
        str(prod_file),
        1,
        "production Actuator exposure must not include wildcard endpoints",
    )]
