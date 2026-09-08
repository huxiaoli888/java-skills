#!/usr/bin/env python3
"""List, sanity-check, and lightly score forward-test scenarios for this skill.

The script keeps scenario files executable and can check whether a human or
subagent output mentions the expected keywords. It is not a semantic grader.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCENARIO_FILE = ROOT / "references" / "forward-test-scenarios.md"
FIXTURE_OUTPUT_DIR = ROOT / "references" / "forward-test-fixtures"
SKILL_NAME = ROOT.name


def zh(hexes: list[int]) -> str:
    return "".join(chr(value) for value in hexes)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_scenarios(text: str) -> list[tuple[str, str]]:
    toc_title = zh([0x76ee, 0x5f55])
    matches = list(re.finditer(r"^##\s+(.+)$", text, re.MULTILINE))
    scenarios: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        title = match.group(1).strip()
        if title == toc_title:
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        scenarios.append((title, text[start:end].strip()))
    return scenarios


def validate_scenarios(scenarios: list[tuple[str, str]]) -> list[str]:
    errors: list[str] = []
    input_text = zh([0x8f93, 0x5165])
    expected_focus_text = zh([0x9884, 0x671f, 0x5173, 0x6ce8, 0x70b9])
    if not scenarios:
        errors.append(zh([0x7f3a, 0x5c11, 0x20, 0x66, 0x6f, 0x72, 0x77, 0x61, 0x72, 0x64, 0x2d, 0x74, 0x65, 0x73, 0x74, 0x20, 0x573a, 0x666f]))
    for title, body in scenarios:
        if input_text not in body and "Input" not in body:
            errors.append(f"{title} " + zh([0x7f3a, 0x5c11, 0x8f93, 0x5165, 0x4efb, 0x52a1, 0x6216, 0x8f93, 0x5165, 0x4ee3, 0x7801, 0x7279, 0x5f81]))
        if expected_focus_text not in body:
            errors.append(f"{title} " + zh([0x7f3a, 0x5c11, 0x9884, 0x671f, 0x5173, 0x6ce8, 0x70b9]))
        if "### Input Sample" not in body:
            errors.append(f"{title} missing Input Sample")
        if "### Expected Findings" not in body:
            errors.append(f"{title} missing Expected Findings")
        expected = body.split("### Expected Findings", 1)[1] if "### Expected Findings" in body else ""
        if expected.count("rule:") < 2:
            errors.append(f"{title} expected findings must include at least two rule entries")
        if "keyword:" not in expected:
            errors.append(f"{title} expected findings must include keyword entries")
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
        if stripped.startswith("keyword:"):
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
    selected = [
        item for item in indexed
        if str(item[0]) == scenario_filter or scenario_filter in item[1]
    ]
    if not selected:
        raise ValueError(f"未找到 forward-test 场景：{scenario_filter}")
    return selected


def score_output(scenarios: list[tuple[str, str]], output_file: Path | None, score_dir: Path | None, min_score: float, scenario_filter: str | None) -> int:
    errors: list[str] = []
    print("\nforward-test 输出评分：")
    for index, title, body in select_scenarios(scenarios, scenario_filter):
        keywords = extract_expected_keywords(body)
        if output_file:
            source = output_file
        elif score_dir:
            source = next((candidate for candidate in output_candidates(score_dir, index, title) if candidate.exists()), None)
            if source is None:
                errors.append(f"{title} 缺少输出文件；可使用 {index}.md、scenario-{index}.md 或同名 .md/.txt")
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
        missing = [keyword for keyword in keywords if keyword not in matched]
        for keyword in missing:
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
    parser.add_argument("--score-fixtures", action="store_true", help="score the bundled expected output fixture")
    parser.add_argument("--scenario", help="score only one scenario by index or title fragment")
    parser.add_argument("--min-score", type=float, default=1.0, help="minimum keyword hit ratio for each scenario")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not SCENARIO_FILE.exists():
        print(zh([0x7f3a, 0x5c11]) + f" {SCENARIO_FILE}", file=sys.stderr)
        return 1
    scenarios = parse_scenarios(read_text(SCENARIO_FILE))
    errors = validate_scenarios(scenarios)
    if errors:
        print(zh([0x66, 0x6f, 0x72, 0x77, 0x61, 0x72, 0x64, 0x2d, 0x74, 0x65, 0x73, 0x74, 0x20, 0x573a, 0x666f, 0x68c0, 0x67e5, 0x5931, 0x8d25, 0xff1a]), file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(zh([0x66, 0x6f, 0x72, 0x77, 0x61, 0x72, 0x64, 0x2d, 0x74, 0x65, 0x73, 0x74, 0x20, 0x573a, 0x666f, 0x68c0, 0x67e5, 0x901a, 0x8fc7, 0xff1a]) + f"{len(scenarios)} " + zh([0x4e2a, 0x573a, 0x666f]))
    for title, _ in scenarios:
        print(f"- {title}")
    if args.prompts:
        print("\n" + zh([0x53ef, 0x6267, 0x884c, 0x20, 0x70, 0x72, 0x6f, 0x6d, 0x70, 0x74, 0x73, 0xff1a]))
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
