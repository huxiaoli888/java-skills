#!/usr/bin/env python3
"""Validate the java-development-principles skill package."""

from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    errors: list[str] = []
    skill_path = ROOT / "SKILL.md"
    detail_path = ROOT / "references" / "detailed-principles.md"
    skill_text = read_text(skill_path)
    detail_text = read_text(detail_path) if detail_path.exists() else ""
    agents_text = read_text(ROOT / "agents" / "openai.yaml")
    scenarios_path = ROOT / "references" / "forward-test-scenarios.md"
    runner_path = ROOT / "scripts" / "run_forward_tests.py"
    scenarios_text = read_text(scenarios_path) if scenarios_path.exists() else ""
    runner_text = read_text(runner_path) if runner_path.exists() else ""
    line_count = len(skill_text.splitlines())

    if line_count > 240:
        errors.append(f"SKILL.md 过长：{line_count} 行；高频原则 skill 应保持瘦身，细则放入 references/")

    for needle in [
        "references/detailed-principles.md",
        "## SOLID 指导",
        "## 事务、异常与日志",
        "## 审查与测试摘要",
        "## 详细引用",
        "references/forward-test-scenarios.md",
        "scripts/run_forward_tests.py",
    ]:
        if needle not in skill_text:
            errors.append(f"SKILL.md 缺少瘦身后的路由摘要：{needle}")

    for needle in [
        "## SOLID 指导",
        "## 事务规则",
        "## 异常规则",
        "## 日志规则",
        "## 常见反模式",
        "## 审查清单",
        "## 测试策略",
    ]:
        if needle not in detail_text:
            errors.append(f"references/detailed-principles.md 缺少详细规则：{needle}")

    for needle in ["policy:", "trigger_keywords:", "SOLID", "单一职责", "事务边界", "日志脱敏"]:
        if needle not in agents_text:
            errors.append(f"agents/openai.yaml 缺少触发关键词：{needle}")

    for needle in ["场景一：巨大 Service 继续加分支", "场景二：事务中远程调用", "场景三：Controller 混合职责", "### Expected Findings", "keyword:"]:
        if needle not in scenarios_text:
            errors.append(f"references/forward-test-scenarios.md 缺少原则前向验证内容：{needle}")

    for needle in ["--score-output", "--score-fixtures", "FIXTURE_OUTPUT_DIR", "keyword:", "SKILL_NAME = ROOT.name"]:
        if needle not in runner_text:
            errors.append(f"scripts/run_forward_tests.py 缺少可评分 forward-test 能力：{needle}")

    if errors:
        print("java-development-principles 技能检查失败：")
        for error in errors:
            print(f"- {error}")
        return 1
    print("java-development-principles 技能检查通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
