#!/usr/bin/env python3
"""List and lightly score forward-test scenarios for this skill."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCENARIO_FILE = ROOT / "references" / "forward-test-scenarios.md"
FIXTURE_OUTPUT_DIR = ROOT / "references" / "forward-test-fixtures"
SKILL_NAME = ROOT.name


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_scenarios(text: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"^##\s+(.+)$", text, re.MULTILINE))
    scenarios: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        scenarios.append((title, text[start:end].strip()))
    return scenarios


def validate_scenarios(scenarios: list[tuple[str, str]]) -> list[str]:
    errors: list[str] = []
    if len(scenarios) < 4:
        errors.append("forward-test 场景至少需要 4 个")
    for title, body in scenarios:
        if "### Input Sample" not in body:
            errors.append(f"{title} missing Input Sample")
        if "### 预期关注点" not in body:
            errors.append(f"{title} 缺少预期关注点")
        if "### Expected Findings" not in body:
            errors.append(f"{title} missing Expected Findings")
            continue
        expected = body.split("### Expected Findings", 1)[1]
        if expected.count("keyword:") < 4:
            errors.append(f"{title} expected findings must include at least four keyword entries")
    return errors


def extract_prompt(body: str) -> str:
    match = re.search(r"```text\n(?P<prompt>[\s\S]*?)\n```", body)
    return match.group("prompt").strip() if match else body.strip()


def extract_expected_keywords(body: str) -> list[str]:
    if "### Expected Findings" not in body:
        return []
    expected = body.split("### Expected Findings", 1)[1]
    keywords: list[str] = []
    for line in expected.splitlines():
        stripped = line.strip()
        if stripped.startswith("- keyword:"):
            keyword = stripped.split("keyword:", 1)[1].strip()
            if keyword:
                keywords.append(keyword)
    return keywords


def keyword_terms(keyword: str) -> list[str]:
    terms = re.findall(r"`([^`]+)`", keyword)
    terms.extend(re.findall(r"\b[xa-zA-Z][a-zA-Z0-9_.-]*\b", keyword))
    expanded: list[str] = []
    for term in terms:
        expanded.extend(part for part in re.split(r"[/|]", term) if part)
    return sorted(set(term for term in expanded if len(term) >= 3))


def keyword_hit(keyword: str, output: str) -> bool:
    if keyword in output:
        return True
    terms = keyword_terms(keyword)
    return bool(terms) and all(term in output for term in terms)


def output_candidates(score_dir: Path, index: int, title: str) -> list[Path]:
    return [
        score_dir / f"{index}.md",
        score_dir / f"{index}.txt",
        score_dir / f"scenario-{index}.md",
        score_dir / f"scenario-{index}.txt",
        score_dir / f"{title}.md",
        score_dir / f"{title}.txt",
    ]


def select_scenarios(scenarios: list[tuple[str, str]], scenario_filter: str | None) -> list[tuple[int, str, str]]:
    indexed = [(index, title, body) for index, (title, body) in enumerate(scenarios, 1)]
    if not scenario_filter:
        return indexed
    selected = [item for item in indexed if str(item[0]) == scenario_filter or scenario_filter in item[1]]
    if not selected:
        raise ValueError(f"未找到 forward-test 场景：{scenario_filter}")
    return selected


def score_output(
    scenarios: list[tuple[str, str]],
    output_file: Path | None,
    score_dir: Path | None,
    min_score: float,
    scenario_filter: str | None,
) -> int:
    errors: list[str] = []
    print("\nforward-test 输出评分：")
    for index, title, body in select_scenarios(scenarios, scenario_filter):
        keywords = extract_expected_keywords(body)
        if output_file:
            source = output_file
        elif score_dir:
            source = next((candidate for candidate in output_candidates(score_dir, index, title) if candidate.exists()), None)
            if source is None:
                errors.append(f"{title} 缺少输出文件")
                continue
        else:
            raise ValueError("必须提供 output_file 或 score_dir")
        if not source.exists():
            errors.append(f"{title} 输出文件不存在：{source}")
            continue
        output = read_text(source)
        matched = [keyword for keyword in keywords if keyword_hit(keyword, output)]
        score = len(matched) / len(keywords) if keywords else 0.0
        print(f"- {title}: {len(matched)}/{len(keywords)} keywords, score={score:.2f}, source={source}")
        for keyword in [keyword for keyword in keywords if keyword not in matched]:
            print(f"  缺少 keyword: {keyword}")
        if score < min_score:
            errors.append(f"{title} keyword 命中率 {score:.2f} 低于阈值 {min_score:.2f}")
    if errors:
        print("\nforward-test 输出评分失败：", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="check and list forward-test scenarios")
    parser.add_argument("--prompts", action="store_true", help="print prompts for human or subagent validation")
    parser.add_argument("--score-output", type=Path, help="score one combined output file against all scenario keywords")
    parser.add_argument("--score-dir", type=Path, help="score per-scenario output files from a directory")
    parser.add_argument("--score-fixtures", action="store_true", help="score bundled expected output fixtures")
    parser.add_argument("--scenario", help="score only one scenario by index or title fragment")
    parser.add_argument("--min-score", type=float, default=1.0, help="minimum keyword hit ratio for each scenario")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not SCENARIO_FILE.exists():
        print(f"缺少 {SCENARIO_FILE}", file=sys.stderr)
        return 1
    scenarios = parse_scenarios(read_text(SCENARIO_FILE))
    errors = validate_scenarios(scenarios)
    if errors:
        print("forward-test 场景检查失败：", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"forward-test 场景检查通过：{len(scenarios)} 个场景")
    for title, _ in scenarios:
        print(f"- {title}")
    if args.prompts:
        print("\n可执行 prompts：")
        for title, body in scenarios:
            print(f"\n## {title}\nUse ${SKILL_NAME} at {ROOT} to solve this task:\n{extract_prompt(body)}")
    score_modes = sum(1 for enabled in [args.score_output, args.score_dir, args.score_fixtures] if enabled)
    if score_modes > 1:
        print("不能同时使用 --score-output、--score-dir 和 --score-fixtures", file=sys.stderr)
        return 1
    if args.score_fixtures:
        return score_output(scenarios, None, FIXTURE_OUTPUT_DIR, args.min_score, args.scenario)
    if args.score_output or args.score_dir:
        return score_output(scenarios, args.score_output, args.score_dir, args.min_score, args.scenario)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
