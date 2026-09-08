#!/usr/bin/env python3
"""Validate the java-multi-module-architecture skill package."""

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
    scaffold_ps1_text = read_text(ROOT / "scripts" / "scaffold-maven-multimodule.ps1")

    required_files = [
        "references/module-boundary-rules.md",
        "references/migration-phases.md",
        "references/spring-boot-version-matrix.md",
        "references/testing-strategy.md",
        "references/forward-test-scenarios.md",
        "scripts/scaffold-maven-multimodule.ps1",
        "scripts/scaffold-maven-multimodule.sh",
        "scripts/validate-maven-modules.ps1",
        "scripts/run_forward_tests.py",
        "templates/parent-pom.xml",
        "templates/child-pom.xml",
        "templates/root-AGENTS.md",
        "templates/module-AGENTS.md",
    ]
    for relative in required_files:
        if not (ROOT / relative).exists():
            errors.append(f"缺少多模块关键文件：{relative}")

    for needle in [
        "## 执行模式",
        "## 模块边界原则",
        "## Maven 基线",
        "## 验证规则",
        "check_java_multi_module_architecture_skill.py",
        "references/forward-test-scenarios.md",
        "scripts/run_forward_tests.py",
        "java-backend-api-standard",
        "java-microservice-dev",
        "java-development-principles",
    ]:
        if needle not in skill_text:
            errors.append(f"SKILL.md 缺少多模块边界或维护说明：{needle}")

    for needle in ["policy:", "trigger_keywords:", "Maven 多模块", "模块边界", "依赖方向", "common"]:
        if needle not in agents_text:
            errors.append(f"agents/openai.yaml 缺少触发关键词：{needle}")

    for needle in ["场景一：多个模块共用同一个数据库", "场景二：请求把业务代码放进 common", "场景三：只想分析模块边界"]:
        if needle not in scenarios_text:
            errors.append(f"references/forward-test-scenarios.md 缺少多模块压力场景：{needle}")

    for needle in ["### Expected Findings", "keyword:"]:
        if needle not in scenarios_text:
            errors.append(f"references/forward-test-scenarios.md 缺少可评分期望：{needle}")

    if not (ROOT / "scripts" / "run_forward_tests.py").exists():
        errors.append("缺少 forward-test runner：scripts/run_forward_tests.py")

    for needle in ["--score-output", "--score-fixtures", "FIXTURE_OUTPUT_DIR", "--min-score", "keyword:", "SKILL_NAME = ROOT.name"]:
        if needle not in runner_text:
            errors.append(f"scripts/run_forward_tests.py 缺少可评分 forward-test 能力：{needle}")

    for needle in ["## 项目概况", "## 模块结构", "## 构建与运行", "## 编码规则", "需确认"]:
        if needle not in scaffold_ps1_text:
            errors.append(f"scripts/scaffold-maven-multimodule.ps1 生成的 AGENTS.md 缺少中文关键项：{needle}")

    for stale in ["Project Overview", "Module Structure", "Module Responsibility", "Coding Rules", "| $_ | $deployable | TODO |"]:
        if stale in scaffold_ps1_text:
            errors.append(f"scripts/scaffold-maven-multimodule.ps1 存在英文或 TODO 生成内容残留：{stale}")

    if errors:
        print("java-multi-module-architecture 技能检查失败：")
        for error in errors:
            print(f"- {error}")
        return 1
    print("java-multi-module-architecture 技能检查通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
