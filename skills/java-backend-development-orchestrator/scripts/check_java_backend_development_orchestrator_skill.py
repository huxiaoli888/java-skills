#!/usr/bin/env python3
"""Validate the java-backend-development-orchestrator skill package."""

from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require(text: str, needle: str, errors: list[str], context: str) -> None:
    if needle not in text:
        errors.append(f"{context} 缺少关键内容：{needle}")


def main() -> int:
    errors: list[str] = []
    skill_text = read_text(ROOT / "SKILL.md")
    agents_text = read_text(ROOT / "agents" / "openai.yaml")
    scenarios_text = read_text(ROOT / "references" / "forward-test-scenarios.md")
    runner_text = read_text(ROOT / "scripts" / "run_forward_tests.py")

    for needle in [
        "## 职责地图",
        "## 路由规则",
        "## 权威规则位置",
        "java-backend-api-standard",
        "java-backend-project-generator",
        "java-multi-module-architecture",
        "java-development-principles",
        "java-microservice-dev",
        "java-code-review",
        "java-incident-fix",
        "netty-handler-dispatcher",
        "vibecoding-knowledge-base",
        "docs/vibecoding",
        "知识库、AGENTS.md 和文档沉淀",
        "references/forward-test-scenarios.md",
        "scripts/run_forward_tests.py",
    ]:
        require(skill_text, needle, errors, "SKILL.md")

    for stale in ["when implementation follows", "as evidence sources", "for hotfix", "after patch", "for module maps"]:
        if stale in skill_text:
            errors.append(f"SKILL.md 存在未中文化路由残留：{stale}")

    for needle in ["policy:", "trigger_keywords:", "统一入口", "选择 skill", "Netty 协议入口", "生产事故", "知识库", "AGENTS.md", "docs/vibecoding"]:
        require(agents_text, needle, errors, "agents/openai.yaml")

    for needle in ["场景一：只改已有接口实现", "场景二：Netty WebSocket 协议设计", "场景三：线上 500 激增", "场景四：补齐 AI 编程知识库"]:
        require(scenarios_text, needle, errors, "references/forward-test-scenarios.md")

    for needle in ["### Expected Findings", "keyword:"]:
        require(scenarios_text, needle, errors, "references/forward-test-scenarios.md")

    if not (ROOT / "scripts" / "run_forward_tests.py").exists():
        errors.append("缺少 forward-test runner：scripts/run_forward_tests.py")

    for needle in ["--score-output", "--score-fixtures", "FIXTURE_OUTPUT_DIR", "--min-score", "keyword:", "SKILL_NAME = ROOT.name"]:
        require(runner_text, needle, errors, "scripts/run_forward_tests.py")

    if errors:
        print("java-backend-development-orchestrator 技能检查失败：")
        for error in errors:
            print(f"- {error}")
        return 1
    print("java-backend-development-orchestrator 技能检查通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
