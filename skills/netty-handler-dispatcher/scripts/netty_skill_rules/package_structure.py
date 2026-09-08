from __future__ import annotations

import re
from pathlib import Path
from typing import Callable


ReadText = Callable[[Path], str]


def _add_error(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_skill_frontmatter(text: str, errors: list[str]) -> str:
    match = re.match(r"---\n(?P<frontmatter>[\s\S]*?)\n---", text)
    if not match:
        _add_error(errors, "SKILL.md 必须包含 YAML frontmatter")
        return ""

    frontmatter = match.group("frontmatter")
    fields: dict[str, str] = {}
    for line_no, line in enumerate(frontmatter.splitlines(), 1):
        if not line.strip():
            continue
        field_match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if not field_match:
            _add_error(errors, f"SKILL.md frontmatter 第 {line_no} 行格式错误：{line}")
            continue
        key, value = field_match.group(1), field_match.group(2)
        if key in fields:
            _add_error(errors, f"SKILL.md frontmatter 字段重复：{key}")
        fields[key] = value

    allowed_fields = {"name", "description"}
    for key in sorted(set(fields) - allowed_fields):
        _add_error(errors, f"SKILL.md frontmatter 不应包含额外字段：{key}")
    for key in ["name", "description"]:
        if key not in fields or not fields[key].strip():
            _add_error(errors, f"SKILL.md frontmatter 缺少必填字段：{key}")
    if fields.get("name") != "netty-handler-dispatcher":
        _add_error(errors, "SKILL.md frontmatter name 必须等于 netty-handler-dispatcher")

    return frontmatter


def validate_skill_tree(root: Path, errors: list[str]) -> None:
    allowed_top_level = {"SKILL.md", "agents", "references", "scripts"}
    forbidden_auxiliary_docs = {
        "README.MD",
        "INSTALLATION_GUIDE.MD",
        "QUICK_REFERENCE.MD",
        "CHANGELOG.MD",
        "NOTES.MD",
        "TODO.MD",
    }
    for child in root.iterdir():
        name = child.name
        if name not in allowed_top_level:
            _add_error(errors, f"技能根目录存在未登记文件或目录：{name}")
        if name.upper() in forbidden_auxiliary_docs:
            _add_error(errors, f"技能根目录不应包含辅助文档：{name}")

    allowed_child_files = {
        "agents": {"openai.yaml"},
        "scripts": {"check_netty_handler_dispatcher_skill.py", "netty_skill_rules", "run_forward_tests.py"},
    }
    for dirname, allowed_names in allowed_child_files.items():
        directory = root / dirname
        if not directory.exists():
            _add_error(errors, f"技能目录缺少子目录：{dirname}")
            continue
        for child in directory.iterdir():
            if child.name not in allowed_names:
                _add_error(errors, f"{dirname}/ 存在未登记文件或目录：{child.name}")

    transient_patterns = [
        r"~$",
        r"\.bak$",
        r"\.tmp$",
        r"\.orig$",
        r"\.rej$",
        r"\.swp$",
        r"\.pyc$",
    ]
    for path in root.rglob("*"):
        relative = path.relative_to(root).as_posix()
        if "__pycache__" in path.parts:
            _add_error(errors, f"技能目录存在 Python 缓存目录：{relative}")
        for pattern in transient_patterns:
            if re.search(pattern, path.name, re.IGNORECASE):
                _add_error(errors, f"技能目录存在临时或备份文件：{relative}")


def validate_agents_openai_yaml(text: str, errors: list[str]) -> None:
    if not re.search(r"^interface:\s*$", text, re.MULTILINE):
        _add_error(errors, "agents/openai.yaml 必须包含顶层 interface")

    allowed_top_level = {"interface", "dependencies", "policy"}
    for match in re.finditer(r"^([A-Za-z_][A-Za-z0-9_-]*):", text, re.MULTILINE):
        key = match.group(1)
        if key not in allowed_top_level:
            _add_error(errors, f"agents/openai.yaml 存在未知顶层字段：{key}")

    values: dict[str, str] = {}
    for field in ["display_name", "short_description", "default_prompt"]:
        match = re.search(rf"^\s+{field}:\s+\"([^\"]+)\"\s*$", text, re.MULTILINE)
        if not match:
            _add_error(errors, f"agents/openai.yaml interface.{field} 必须存在且使用双引号字符串")
            continue
        values[field] = match.group(1)

    if display_name := values.get("display_name"):
        if not (3 <= len(display_name) <= 64):
            _add_error(errors, "agents/openai.yaml interface.display_name 长度应为 3-64 字符")

    if short_description := values.get("short_description"):
        if not (12 <= len(short_description) <= 64):
            _add_error(errors, "agents/openai.yaml interface.short_description 应保持 12-64 字符，便于 UI 快速扫描")

    if default_prompt := values.get("default_prompt"):
        allowed_prefixes = (
            "使用 $netty-handler-dispatcher ",
            "Use $netty-handler-dispatcher ",
        )
        if not default_prompt.startswith(allowed_prefixes):
            _add_error(errors, "agents/openai.yaml interface.default_prompt 必须以“使用 $netty-handler-dispatcher ”或“Use $netty-handler-dispatcher ”开头")
        if default_prompt.count("。") > 1:
            _add_error(errors, "agents/openai.yaml interface.default_prompt 应保持一条简短示例 prompt")
        if len(default_prompt) > 220:
            _add_error(errors, "agents/openai.yaml interface.default_prompt 过长，应保持简短")


def validate_agents_skill_capabilities(agents_text: str, errors: list[str]) -> None:
    if "$netty-handler-dispatcher" not in agents_text:
        _add_error(errors, "agents/openai.yaml default_prompt 必须包含技能名称")
    if "Legacy" in agents_text or "allow_implicit_invocation: false" in agents_text:
        _add_error(errors, "agents/openai.yaml 不应描述为历史兼容技能")
    if "签名路由" in agents_text:
        _add_error(errors, "agents/openai.yaml 不应把签名防重放和集群路由合并成含混的“签名路由”")
    for text in [
        "协议入口",
        "分发",
        "连接治理",
        "TCP/UDP/WebSocket",
        "handler dispatcher",
        "func + version 分发",
        "令牌上传/下载",
        "心跳",
        "ACK",
        "签名",
        "防重放",
        "集群路由",
        "背压",
        "压测",
    ]:
        if text not in agents_text:
            _add_error(errors, f"agents/openai.yaml 必须准确描述技能触发能力：{text}")
    if "UDP/TCP/WebSocket 长连接消息" in agents_text:
        _add_error(errors, "agents/openai.yaml 不应把 UDP/TCP/WebSocket 统称为长连接消息")


def validate_agents_file(root: Path, read_text: ReadText, errors: list[str]) -> None:
    agents_yaml = root / "agents" / "openai.yaml"
    if not agents_yaml.exists():
        _add_error(errors, "缺少 agents/openai.yaml")
        return
    agents_text = read_text(agents_yaml)
    validate_agents_openai_yaml(agents_text, errors)
    validate_agents_skill_capabilities(agents_text, errors)
