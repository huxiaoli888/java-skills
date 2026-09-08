#!/usr/bin/env python3
"""Validate the java-code-review skill package."""

from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    errors: list[str] = []
    skill_text = read_text(ROOT / "SKILL.md")
    agents_text = read_text(ROOT / "agents" / "openai.yaml")
    scenarios_text = read_text(ROOT / "references" / "forward-test-scenarios.md")
    runner_text = read_text(ROOT / "scripts" / "run_forward_tests.py")
    reference_texts = {
        "references/testing-review.md": read_text(ROOT / "references" / "testing-review.md"),
        "references/security-review.md": read_text(ROOT / "references" / "security-review.md"),
        "references/microservice-review.md": read_text(ROOT / "references" / "microservice-review.md"),
        "references/data-consistency-review.md": read_text(ROOT / "references" / "data-consistency-review.md"),
    }

    for needle in [
        "## 审查流程",
        "## 严重级别",
        "## 输出格式",
        "[P1] 简短标题",
        "位置:",
        "证据:",
        "影响:",
        "修复:",
        "建议测试:",
        "置信度:",
        "Test Gaps:",
        "Commands Run:",
        "No critical findings.",
        "references/forward-test-scenarios.md",
        "scripts/run_forward_tests.py",
    ]:
        if needle not in skill_text:
            errors.append(f"SKILL.md 缺少代码审查输出契约：{needle}")

    for needle in ["policy:", "trigger_keywords:", "代码审查", "PR", "diff", "Finding", "测试缺口"]:
        if needle not in agents_text:
            errors.append(f"agents/openai.yaml 缺少触发关键词：{needle}")

    for needle in ["场景一：PR 同时改 Controller 和 Service", "场景二：证据不足的性能猜测", "场景三：无问题但测试缺口存在"]:
        if needle not in scenarios_text:
            errors.append(f"references/forward-test-scenarios.md 缺少审查压力场景：{needle}")

    for needle in ["### Expected Findings", "keyword:"]:
        if needle not in scenarios_text:
            errors.append(f"references/forward-test-scenarios.md 缺少可评分期望：{needle}")

    if not (ROOT / "scripts" / "run_forward_tests.py").exists():
        errors.append("缺少 forward-test runner：scripts/run_forward_tests.py")

    for needle in ["--score-output", "--score-fixtures", "FIXTURE_OUTPUT_DIR", "--min-score", "keyword:", "SKILL_NAME = ROOT.name"]:
        if needle not in runner_text:
            errors.append(f"scripts/run_forward_tests.py 缺少可评分 forward-test 能力：{needle}")

    reference_needles = {
        "references/testing-review.md": ["# 测试审查参考", "## 按变更类型判断测试期望", "缺少测试"],
        "references/security-review.md": ["# 安全审查参考", "## 认证与授权", "## 签名、加密与防重放"],
        "references/microservice-review.md": ["# 微服务审查参考", "## Feign / RPC / 外部调用", "## MQ 生产者 / 消费者"],
        "references/data-consistency-review.md": ["# 数据一致性审查参考", "## 事务边界", "## DB + MQ 一致性"],
    }
    for relative, needles in reference_needles.items():
        for needle in needles:
            if needle not in reference_texts[relative]:
                errors.append(f"{relative} 缺少中文引用关键项：{needle}")

    for relative, reference_text in reference_texts.items():
        for stale in ["Use this reference", "Review Reference", "Check:", "Risk signs:"]:
            if stale in reference_text:
                errors.append(f"{relative} 存在英文引用残留：{stale}")

    if errors:
        print("java-code-review 技能检查失败：")
        for error in errors:
            print(f"- {error}")
        return 1
    print("java-code-review 技能检查通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
