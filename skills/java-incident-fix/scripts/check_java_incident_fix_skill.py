#!/usr/bin/env python3
"""Validate the java-incident-fix skill package."""

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
    template_texts = {
        "templates/incident-runbook.md": read_text(ROOT / "templates" / "incident-runbook.md"),
        "templates/incident-timeline.md": read_text(ROOT / "templates" / "incident-timeline.md"),
        "templates/rca-report.md": read_text(ROOT / "templates" / "rca-report.md"),
        "templates/hotfix-plan.md": read_text(ROOT / "templates" / "hotfix-plan.md"),
        "templates/rollback-plan.md": read_text(ROOT / "templates" / "rollback-plan.md"),
    }
    reference_texts = {
        "references/jvm-incident.md": read_text(ROOT / "references" / "jvm-incident.md"),
        "references/db-incident.md": read_text(ROOT / "references" / "db-incident.md"),
        "references/mq-redis-incident.md": read_text(ROOT / "references" / "mq-redis-incident.md"),
        "references/external-config-incident.md": read_text(ROOT / "references" / "external-config-incident.md"),
        "references/security-crypto-incident.md": read_text(ROOT / "references" / "security-crypto-incident.md"),
    }

    for needle in [
        "## 事故类型路由",
        "## 证据采集",
        "## 专项引用",
        "## 数据修复规则",
        "## 回滚 / 热修复决策树",
        "## 恢复验证",
        "references/forward-test-scenarios.md",
        "scripts/run_forward_tests.py",
        "止血",
        "RCA",
    ]:
        if needle not in skill_text:
            errors.append(f"SKILL.md 缺少事故处理规则：{needle}")

    for stale in ["Incident Type Routing", "Evidence To Capture", "Specialist References", "Data Repair Rules", "Many HTTP 500 errors"]:
        if stale in skill_text:
            errors.append(f"SKILL.md 存在英文残留：{stale}")

    for needle in [
        "用只读查询确认影响范围",
        "备份受影响数据",
        "准备可幂等执行的数据修复 SQL 或脚本",
    ]:
        if needle not in skill_text:
            errors.append(f"SKILL.md 数据修复规则未中文化或缺少关键步骤：{needle}")

    template_needles = {
        "templates/incident-runbook.md": ["# 事故处理运行手册", "## 事故概况", "## 即时动作", "## 止血选项", "## 恢复验证"],
        "templates/incident-timeline.md": ["# 事故时间线", "发现事故", "首次止血", "确认根因", "验证恢复"],
        "templates/rca-report.md": ["# 根因分析报告", "## 触发因素", "## 根因", "## 预防动作"],
        "templates/hotfix-plan.md": ["# 热修复计划", "## 修复范围", "## 补丁策略", "## 发布计划"],
        "templates/rollback-plan.md": ["# 回滚计划", "## 回滚目标", "## 前置条件", "## 中止条件"],
    }
    for relative, needles in template_needles.items():
        for needle in needles:
            if needle not in template_texts[relative]:
                errors.append(f"{relative} 缺少中文模板关键项：{needle}")

    for relative, template_text in template_texts.items():
        for stale in ["Incident Summary", "Immediate Actions", "Root Cause Analysis", "Hotfix Plan", "Rollback Plan"]:
            if stale in template_text:
                errors.append(f"{relative} 存在英文模板残留：{stale}")

    reference_needles = {
        "references/jvm-incident.md": ["# JVM 事故参考", "## 需要采集的证据", "## 常见原因", "## 止血"],
        "references/db-incident.md": ["# 数据库事故参考", "## 数据修复保护", "## 代码复核点"],
        "references/mq-redis-incident.md": ["# MQ 与 Redis 事故参考", "## MQ 止血", "## Redis 止血"],
        "references/external-config-incident.md": ["# 外部调用与配置事故参考", "## 外部调用证据", "## 配置止血"],
        "references/security-crypto-incident.md": ["# 安全与密码事故参考", "## 即时动作", "## 密码流程检查"],
    }
    for relative, needles in reference_needles.items():
        for needle in needles:
            if needle not in reference_texts[relative]:
                errors.append(f"{relative} 缺少中文引用关键项：{needle}")

    for relative, reference_text in reference_texts.items():
        for stale in ["Incident Reference", "Evidence To Collect", "Common Causes", "Mitigation", "Verification"]:
            if stale in reference_text:
                errors.append(f"{relative} 存在英文引用残留：{stale}")

    for needle in ["policy:", "trigger_keywords:", "生产事故", "500 激增", "止血", "根因定位", "RCA"]:
        if needle not in agents_text:
            errors.append(f"agents/openai.yaml 缺少触发关键词：{needle}")

    for needle in ["场景一：发布后 HTTP 500 激增", "场景二：数据修复请求", "场景三：安全密码事件"]:
        if needle not in scenarios_text:
            errors.append(f"references/forward-test-scenarios.md 缺少事故压力场景：{needle}")

    for needle in ["### Expected Findings", "keyword:"]:
        if needle not in scenarios_text:
            errors.append(f"references/forward-test-scenarios.md 缺少可评分期望：{needle}")

    if not (ROOT / "scripts" / "run_forward_tests.py").exists():
        errors.append("缺少 forward-test runner：scripts/run_forward_tests.py")

    for needle in ["--score-output", "--score-fixtures", "FIXTURE_OUTPUT_DIR", "--min-score", "keyword:", "SKILL_NAME = ROOT.name"]:
        if needle not in runner_text:
            errors.append(f"scripts/run_forward_tests.py 缺少可评分 forward-test 能力：{needle}")

    if errors:
        print("java-incident-fix 技能检查失败：")
        for error in errors:
            print(f"- {error}")
        return 1
    print("java-incident-fix 技能检查通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
