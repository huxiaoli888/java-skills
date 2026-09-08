#!/usr/bin/env python3
"""Self-check for the vibecoding knowledge-base skill."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
AGENT = ROOT / "agents" / "openai.yaml"
REFERENCES = {
    "mode": ROOT / "references" / "mode-update-rules.md",
    "templates": ROOT / "references" / "document-templates.md",
    "quality": ROOT / "references" / "delivery-quality-rules.md",
    "forward": ROOT / "references" / "forward-test-scenarios.md",
}
RUNNER = ROOT / "scripts" / "run_forward_tests.py"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    errors: list[str] = []

    for path in [SKILL, AGENT, RUNNER, *REFERENCES.values()]:
        require(errors, path.exists(), f"缺少文件：{path}")
    if errors:
        return report(errors)

    skill = read(SKILL)
    agent = read(AGENT)
    runner = read(RUNNER)
    refs = {name: read(path) for name, path in REFERENCES.items()}

    require(errors, "name: vibecoding-knowledge-base" in skill, "SKILL.md frontmatter 缺少正确 name")
    description_match = re.search(r"^description:\s*(.+)$", skill, re.MULTILINE)
    require(errors, bool(description_match), "SKILL.md frontmatter 缺少 description")
    if description_match:
        require(errors, description_match.group(1).startswith("Use when"), "description 必须以 Use when 开头")
        require(errors, len(description_match.group(1)) <= 500, "description 建议不超过 500 字符")

    for heading in ["## 概述", "## 硬性边界", "## 执行模式", "## 引用路由", "## 质量底线", "## 完整分析门禁", "## 文档自检"]:
        require(errors, heading in skill, f"SKILL.md 缺少章节：{heading}")
    for reference_name in ["references/mode-update-rules.md", "references/document-templates.md", "references/delivery-quality-rules.md", "references/forward-test-scenarios.md"]:
        require(errors, reference_name in skill, f"SKILL.md 未路由引用：{reference_name}")
    for stale in ["## Hard Boundaries", "## Reference Files", "Use this skill", "All generated prose"]:
        require(errors, stale not in skill, f"SKILL.md 存在旧英文入口内容：{stale}")
    require(errors, len(skill.split()) < 1000, "SKILL.md 仍然过长，应保持为入口而非完整参考手册")

    zh_duplicates = [path for path in ROOT.rglob("*_zh.*") if path.is_file()]
    require(errors, not zh_duplicates, "仍存在 _zh 双轨副本：" + ", ".join(str(path) for path in zh_duplicates))

    require(errors, "policy:" in agent, "agents/openai.yaml 缺少 policy")
    require(errors, "trigger_keywords:" in agent, "agents/openai.yaml 缺少 trigger_keywords")
    for keyword in ["知识库", "AGENTS.md", "docs/vibecoding", "待确认清单", "跨仓边界"]:
        require(errors, keyword in agent, f"agents/openai.yaml 缺少触发词：{keyword}")
    require(errors, "$vibecoding-knowledge-base" in agent, "agents/openai.yaml default_prompt 必须显式包含技能名")

    require(errors, refs["mode"].startswith("# 模式与更新规则"), "mode-update-rules.md 未使用中文权威文件")
    require(errors, refs["templates"].startswith("# 文档模板"), "document-templates.md 未使用中文权威文件")
    require(errors, refs["quality"].startswith("# 交付与质量规则"), "delivery-quality-rules.md 未使用中文权威文件")
    for name, text in refs.items():
        require(errors, "待确认" in text, f"{name} 引用文件缺少待确认治理关键词")

    for scenario in ["快速项目导航", "完整补齐知识库", "已有知识库变更", "跨仓依赖"]:
        require(errors, scenario in refs["forward"], f"forward-test 缺少场景：{scenario}")
    require(errors, refs["forward"].count("### Expected Findings") >= 4, "forward-test 场景数量不足")
    require(errors, refs["forward"].count("keyword:") >= 16, "forward-test keyword 覆盖不足")

    for token in ["--score-output", "--score-fixtures", "FIXTURE_OUTPUT_DIR", "--min-score", "SKILL_NAME = ROOT.name"]:
        require(errors, token in runner, f"run_forward_tests.py 缺少能力：{token}")

    generated_dirs = [ROOT / "__pycache__", ROOT / ".pytest_cache", ROOT / "target"]
    require(errors, not any(path.exists() for path in generated_dirs), "skill 目录存在生成目录，应清理后再发布")

    return report(errors)


def report(errors: list[str]) -> int:
    if errors:
        print("vibecoding skill 自检失败：", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("vibecoding skill 自检通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
