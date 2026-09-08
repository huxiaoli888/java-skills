#!/usr/bin/env python3
"""Validate the java-backend-api-standard skill package itself."""

from __future__ import annotations

import re
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
ALLOWED_ROOT_ENTRIES = {"SKILL.md", "agents", "references", "scripts"}
FORBIDDEN_AUXILIARY_DOCS = {
    "README.md",
    "INSTALLATION_GUIDE.md",
    "QUICK_REFERENCE.md",
    "CHANGELOG.md",
    "TODO.md",
}
REQUIRED_RULE_TEXT = [
    "正常业务失败与程序异常边界",
    "business-exception-control-flow",
    "scripts/check_java_backend_api_standard_skill.py",
    "正常业务失败不应在 service/domain/application 层通过 BusinessException 作为常规控制流",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def add_error(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_frontmatter(skill_text: str, errors: list[str]) -> None:
    if not skill_text.startswith("---\n"):
        add_error(errors, "SKILL.md 必须包含 YAML frontmatter")
        return
    end = skill_text.find("\n---", 4)
    if end < 0:
        add_error(errors, "SKILL.md frontmatter 未闭合")
        return
    frontmatter = skill_text[4:end].strip().splitlines()
    fields: dict[str, str] = {}
    for line_no, line in enumerate(frontmatter, 2):
        if not re.match(r"^[a-zA-Z0-9_-]+:\s*.+$", line):
            add_error(errors, f"SKILL.md frontmatter 第 {line_no} 行格式错误：{line}")
            continue
        key, value = line.split(":", 1)
        if key in fields:
            add_error(errors, f"SKILL.md frontmatter 字段重复：{key}")
        fields[key] = value.strip()
    for key in fields:
        if key not in {"name", "description"}:
            add_error(errors, f"SKILL.md frontmatter 不应包含额外字段：{key}")
    for key in ["name", "description"]:
        if key not in fields:
            add_error(errors, f"SKILL.md frontmatter 缺少必填字段：{key}")
    if fields.get("name") != "java-backend-api-standard":
        add_error(errors, "SKILL.md frontmatter name 必须等于 java-backend-api-standard")


def validate_tree(errors: list[str]) -> None:
    for child in SKILL_ROOT.iterdir():
        if child.name not in ALLOWED_ROOT_ENTRIES:
            add_error(errors, f"技能根目录存在未登记文件或目录：{child.name}")
        if child.name.upper() in {name.upper() for name in FORBIDDEN_AUXILIARY_DOCS}:
            add_error(errors, f"技能根目录不应包含辅助文档：{child.name}")
    for required_dir in ["agents", "references", "scripts"]:
        if not (SKILL_ROOT / required_dir).is_dir():
            add_error(errors, f"技能目录缺少子目录：{required_dir}")
    for path in SKILL_ROOT.rglob("*"):
        if "__pycache__" in path.parts:
            add_error(errors, f"技能目录存在 Python 缓存目录：{path.relative_to(SKILL_ROOT)}")


def validate_agents(errors: list[str]) -> None:
    path = SKILL_ROOT / "agents" / "openai.yaml"
    if not path.exists():
        add_error(errors, "缺少 agents/openai.yaml")
        return
    text = read_text(path)
    for field in ["display_name", "short_description", "default_prompt"]:
        if f"{field}:" not in text:
            add_error(errors, f"agents/openai.yaml 缺少 interface.{field}")
    if "$java-backend-api-standard" not in text:
        add_error(errors, "agents/openai.yaml default_prompt 必须包含技能名称")


def validate_references(skill_text: str, errors: list[str]) -> None:
    for match in re.finditer(r"`(references/[^`]+)`", skill_text):
        rel = match.group(1)
        if not (SKILL_ROOT / rel).exists():
            add_error(errors, f"SKILL.md 引用的资源不存在：{rel}")
    for ref in (SKILL_ROOT / "references").glob("*.md"):
        lines = read_text(ref).splitlines()
        if len(lines) > 100:
            first_block = "\n".join(lines[:30])
            if "## 目录" not in first_block:
                add_error(errors, f"长 reference 缺少目录：{ref.name}")


def validate_required_rules(all_text: str, errors: list[str]) -> None:
    for text in REQUIRED_RULE_TEXT:
        if text not in all_text:
            add_error(errors, f"缺少关键规则文本：{text}")
    if '"BusinessException.java": "business exception is missing"' in all_text:
        add_error(errors, "检查器不应继续强制要求 BusinessException.java")
    if "将领域错误转换为带错误码的业务异常" in all_text:
        add_error(errors, "分层规则不应继续要求领域错误转换为业务异常")


def validate_skill_summary(skill_text: str, errors: list[str]) -> None:
    expected = "受保护接口同时要求 `x-timestamp`、`x-sign` 防篡改签名、`x-sign-alg` 签名算法和 `x-api-version` 契约版本"
    if expected not in skill_text:
        add_error(errors, "SKILL.md 基础内部 API 摘要必须包含 x-timestamp，避免和 CMS 防重放规则不一致")
    expected_replay = "`x-timestamp` 校验时间窗口，使用 `x-api-key + x-reqid` 作为防重放键"
    if expected_replay not in skill_text:
        add_error(errors, "SKILL.md 公开客户端 API 摘要必须区分 x-timestamp 时间窗口和 x-api-key + x-reqid replay key")
    if "防重放使用 `x-timestamp` 和 `x-reqid`" in skill_text:
        add_error(errors, "SKILL.md 不应继续把 x-timestamp 描述为 replay key 的组成部分")
    refined_design_principle = "在需要的边界增加 `x-timestamp` 时间窗口校验、`x-sign` 防篡改签名、按调用方拆分的 replay key 防重放和业务幂等"
    if refined_design_principle not in skill_text:
        add_error(errors, "SKILL.md 设计原则必须区分 x-timestamp 时间窗口、x-sign 防篡改和按调用方拆分的 replay key")
    if "`x-sign` 防篡改签名、`x-reqid` 防重放" in skill_text:
        add_error(errors, "SKILL.md 设计原则不应继续把 x-reqid 单独称为防重放机制")


def validate_signature_contract(errors: list[str]) -> None:
    contract_text = read_text(SKILL_ROOT / "references" / "api-standard-contract.json")
    security_text = read_text(SKILL_ROOT / "references" / "security.md")
    api_contract_text = read_text(SKILL_ROOT / "references" / "api-contract.md")
    authz_text = read_text(SKILL_ROOT / "references" / "authz-standard.md")
    production_replacement_text = read_text(SKILL_ROOT / "references" / "production-replacement.md")
    checker_coverage_text = read_text(SKILL_ROOT / "references" / "checker-coverage-matrix.md")
    if '"common": [\n      "authorization",\n      "accept-language",\n      "x-trace-id",\n      "x-reqid",\n      "x-timestamp",' not in contract_text:
        add_error(errors, "references/api-standard-contract.json 必须把 x-timestamp 放入 requestHeaders.common")
    if '"sdkOnly": ["x-api-key", "x-timestamp"]' in contract_text:
        add_error(errors, "references/api-standard-contract.json 不应把 x-timestamp 放在 sdkOnly，CMS 受保护接口也依赖它防重放")
    refined_replay_summary = "敏感 API 使用 `x-timestamp` 校验时间窗口，使用按调用方类型拆分的 replay key 防重放，不再使用 `x-nonce`。"
    if refined_replay_summary not in security_text:
        add_error(errors, "references/security.md 必须区分 x-timestamp 时间窗口校验和按调用方拆分的 replay key")
    if "敏感 API 使用 `x-timestamp` 和 `x-reqid` 做防重放" in security_text:
        add_error(errors, "references/security.md 不应继续把 x-timestamp 和 x-reqid 混称为完整防重放机制")
    if "受保护接口同时要求 `x-timestamp` 时间窗口校验、`x-sign` 防篡改签名、`x-sign-alg` 签名算法和 `x-api-version` 契约版本" not in authz_text:
        add_error(errors, "references/authz-standard.md 的 CMS 受保护接口摘要必须包含 x-timestamp 时间窗口校验")
    if "CMS 和 SDK 受保护接口都已要求 `x-timestamp`、`x-sign`、`x-sign-alg` 和 `x-api-version`" not in production_replacement_text:
        add_error(errors, "references/production-replacement.md 上线前验证必须包含 x-timestamp")
    if "`x-reqid` 重放窗口" in production_replacement_text:
        add_error(errors, "references/production-replacement.md 不应把 x-reqid 单独描述为重放窗口")
    if "检查 `x-reqid`、`x-timestamp`、`x-udid`、`x-sign`、`x-sign-alg`、`x-api-version`" not in checker_coverage_text:
        add_error(errors, "references/checker-coverage-matrix.md 请求头和签名覆盖范围必须包含 x-timestamp 和 x-udid")
    common_header_section = re.search(
        r"通用请求头：\n\n```text\n(?P<body>.*?)\n```",
        api_contract_text,
        re.DOTALL,
    )
    if not common_header_section:
        add_error(errors, "references/api-contract.md 必须声明通用请求头代码块")
    elif "x-timestamp:" not in common_header_section.group("body"):
        add_error(errors, "references/api-contract.md 通用请求头必须包含 x-timestamp，和 api-standard-contract.json 保持一致")
    for file_name, text in {
        "references/security.md": security_text,
        "references/api-contract.md": api_contract_text,
    }.items():
        if "x-timestamp;x-reqid;x-api-key;x-udid;x-sign-alg;x-api-version" not in text:
            add_error(errors, f"{file_name} 必须声明 SDK 签名 canonical 覆盖 x-udid")
        if "x-timestamp;x-reqid;x-api-key;x-sign-alg;x-api-version" in text:
            add_error(errors, f"{file_name} 不应继续保留缺少 x-udid 的 SDK signed headers 顺序")
    public_extra_section = re.search(
        r"公开客户端、H5、移动端、开放平台、支付、回调 API.*?```text\n(?P<body>.*?)\n```",
        api_contract_text,
        re.DOTALL,
    )
    if not public_extra_section:
        add_error(errors, "references/api-contract.md 必须声明公开客户端在通用请求头基础上的额外请求头")
    else:
        extra_body = public_extra_section.group("body")
        if "x-api-key: 客户端应用 key" not in extra_body:
            add_error(errors, "references/api-contract.md 公开客户端额外请求头必须保留 x-api-key")
        for header in ["x-timestamp:", "x-sign:", "x-sign-alg:", "x-api-version:"]:
            if header in extra_body:
                add_error(errors, f"references/api-contract.md 不应把通用请求头 {header[:-1]} 重复列入公开客户端额外请求头")


def validate_forward_runner(errors: list[str]) -> None:
    runner = SKILL_ROOT / "scripts" / "run_forward_tests.py"
    fixture_dir = SKILL_ROOT / "references" / "forward-test-fixtures"
    if not runner.exists():
        add_error(errors, "缺少 forward-test runner：scripts/run_forward_tests.py")
        return
    runner_text = read_text(runner)
    for needle in ["--score-output", "--score-dir", "--score-fixtures", "FIXTURE_OUTPUT_DIR"]:
        if needle not in runner_text:
            add_error(errors, f"scripts/run_forward_tests.py 缺少按场景 fixture 评分能力：{needle}")
    if "FIXTURE_OUTPUT_FILE" in runner_text:
        add_error(errors, "scripts/run_forward_tests.py 的 --score-fixtures 不应继续使用合并 expected-output.md 评分")
    if (fixture_dir / "expected-output.md").exists():
        add_error(errors, "references/forward-test-fixtures/expected-output.md 已废弃，应使用 scenario-N.md")
    for index in range(1, 4):
        if not (fixture_dir / f"scenario-{index}.md").exists():
            add_error(errors, f"缺少按场景 forward-test fixture：references/forward-test-fixtures/scenario-{index}.md")


def collect_text() -> str:
    chunks: list[str] = []
    for path in [SKILL_ROOT / "SKILL.md", *sorted((SKILL_ROOT / "references").glob("*.md")), *sorted((SKILL_ROOT / "scripts").rglob("*.py"))]:
        if path.name == "check_java_backend_api_standard_skill.py":
            continue
        chunks.append(read_text(path))
    return "\n".join(chunks)


def main() -> int:
    errors: list[str] = []
    skill_text = read_text(SKILL_ROOT / "SKILL.md")
    validate_frontmatter(skill_text, errors)
    validate_tree(errors)
    validate_agents(errors)
    validate_references(skill_text, errors)
    validate_required_rules(collect_text(), errors)
    validate_skill_summary(skill_text, errors)
    validate_signature_contract(errors)
    validate_forward_runner(errors)

    if errors:
        print("java-backend-api-standard 技能检查失败：")
        for error in errors:
            print(f"- {error}")
        return 1
    print("java-backend-api-standard 技能检查通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
