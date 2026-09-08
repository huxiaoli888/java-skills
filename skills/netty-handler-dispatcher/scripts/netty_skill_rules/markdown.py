from __future__ import annotations

import re
import unicodedata


def _add_error(errors: list[str], message: str) -> None:
    errors.append(message)


def markdown_anchor(title: str) -> str:
    anchor = title.strip().lower()
    anchor = anchor.replace("`", "")
    chars: list[str] = []
    for ch in anchor:
        if unicodedata.category(ch).startswith("P"):
            continue
        chars.append(ch)
    anchor = "".join(chars)
    anchor = re.sub(r"\s+", "-", anchor)
    return anchor


def validate_toc_anchors(name: str, text: str, errors: list[str]) -> None:
    headings = {
        markdown_anchor(match.group(1))
        for match in re.finditer(r"^##\s+(.+)$", text, re.MULTILINE)
    }
    for link_text, anchor in re.findall(r"^- \[([^\]]+)\]\(#([^)]+)\)", text, re.MULTILINE):
        if anchor not in headings:
            _add_error(errors, f"{name} 目录锚点失效：{link_text} -> #{anchor}")


def validate_markdown_fences(name: str, text: str, errors: list[str]) -> None:
    open_fence: tuple[str, int, int] | None = None
    opener_pattern = re.compile(r"^ {0,3}(`{3,}|~{3,}).*$")
    for line_no, line in enumerate(text.splitlines(), 1):
        if open_fence is None:
            match = opener_pattern.match(line)
            if match:
                fence = match.group(1)
                open_fence = (fence[0], len(fence), line_no)
            continue

        fence_char, fence_length, start_line = open_fence
        close_pattern = rf"^ {{0,3}}{re.escape(fence_char) * fence_length}{re.escape(fence_char)}*\s*$"
        if re.match(close_pattern, line):
            open_fence = None

    if open_fence is not None:
        fence_char, fence_length, start_line = open_fence
        _add_error(errors, f"{name} 第 {start_line} 行存在未闭合的 Markdown fence：{fence_char * fence_length}")


def validate_templates_markdown(text: str, errors: list[str]) -> None:
    allowed_real_headings = {
        "# 输出模板",
        "## 目录",
        "## 模板维护边界",
        "## 模板索引",
        "## 设计评审模板",
        "## ADR 模板",
        "## Netty 传输协议说明书模板",
        "## 集群路由设计模板",
        "## 压测报告模板",
    }
    in_template_fence = False
    for line_no, line in enumerate(text.splitlines(), 1):
        if line.startswith("````"):
            in_template_fence = not in_template_fence
            continue
        if not in_template_fence and line.startswith("#") and line.strip() not in allowed_real_headings:
            _add_error(errors, f"templates.md 第 {line_no} 行存在泄漏的模板标题：{line.strip()}")
    if in_template_fence:
        _add_error(errors, "templates.md 存在未闭合的四反引号模板代码块")


def validate_no_unresolved_placeholders(name: str, text: str, errors: list[str]) -> None:
    for line_no, line in enumerate(text.splitlines(), 1):
        if re.search(r"(^|\s)(?:\.\.\.|…)(\s|$)", line):
            _add_error(errors, f"{name} 第 {line_no} 行存在未替换的省略号占位：{line.strip()}")
        if re.search(r"\bXxx[A-Za-z0-9_]*\b", line, re.IGNORECASE):
            _add_error(errors, f"{name} 第 {line_no} 行存在 Xxx 风格占位命名：{line.strip()}")
