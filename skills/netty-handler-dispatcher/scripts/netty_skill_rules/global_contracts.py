"""Global markdown and error-code contract checks for the Netty skill."""

from __future__ import annotations

import re

from netty_skill_rules.markdown import (
    validate_markdown_fences,
    validate_no_unresolved_placeholders,
)

FORBIDDEN_NUMERIC_CODES = [
    "100001",
    "100002",
    "100003",
    "100004",
    "100005",
    "100999",
    "S00999",
]


def add_error(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_error_code_literals(text: str, errors: list[str]) -> None:
    allowed = {"000000", "SMEEEE"}
    candidates: set[str] = set()
    candidates.update(re.findall(r'"code"\s*:\s*"([A-Za-z0-9_-]+)"', text))
    candidates.update(re.findall(r"code=([A-Za-z0-9_-]+)", text))
    for numeric_code in re.findall(r'"code"\s*:\s*([0-9]+)', text):
        add_error(errors, f"响应 code 必须是字符串，不能使用数字类型：{numeric_code}")
    error_code_context = re.compile(r"错误码|响应|ACK|失败|成功|返回|拒绝|参数错误|鉴权失败|版本不支持")
    for line in text.splitlines():
        if error_code_context.search(line):
            candidates.update(re.findall(r"`([A-Z0-9]{6})`", line))
    for code in sorted(candidates - allowed):
        if not re.fullmatch(r"[A-Z]{2}\d{4}", code):
            add_error(errors, f"响应错误码字面量不符合 000000 或 SMEEEE 格式：{code}")


def validate_all_markdown_contracts(all_markdown: str, errors: list[str], required_text: list[str]) -> None:
    for code in FORBIDDEN_NUMERIC_CODES:
        if code in all_markdown:
            add_error(errors, f"仍存在旧数字错误码：{code}")
    validate_error_code_literals(all_markdown, errors)

    legacy_misspelled_name = "netty-handler-" + "dispather"
    forbidden_text = [
        legacy_misspelled_name,
        "data.status",
        "ws:conn",
        "ws:user",
        "ws:device",
        "ws:node",
        "ws:notify",
        "ws:stream",
    ]
    for text in forbidden_text:
        if text in all_markdown:
            add_error(errors, f"仍存在过期文本：{text}")
    if "reqid/sequence" in all_markdown:
        add_error(errors, "仍存在旧顺序字段表述 reqid/sequence，应统一为 reqid/seqno 或业务顺序字段 seqno")
    if "code/message/data/ts" in all_markdown:
        add_error(errors, "仍存在旧响应字段顺序 code/message/data/ts，应统一为 reqid/code/message/ts/data")
    if "`reqid` 在同一连接内必须唯一" in all_markdown:
        add_error(errors, "reqid 唯一性不应只按同一连接描述，必须覆盖 HTTP/UDP replay key 或业务幂等维度")
    if "、`sequence`" in all_markdown or "`sequence` 或" in all_markdown:
        add_error(errors, "仍存在旧顺序字段 sequence，应统一为 seqno")
    if "TCP_AUTH" in all_markdown:
        add_error(errors, "仍存在旧认证 func TCP_AUTH，应统一为 AUTH")
    if "禁止吞异常" not in all_markdown:
        add_error(errors, "缺少异常处理规则：必须明确禁止吞异常")
    if "log.error" not in all_markdown:
        add_error(errors, "缺少异常处理规则：当前层处理异常时必须使用 log.error")
    for text in [
        "正常协议拒绝和业务失败使用稳定错误码",
        "正常协议拒绝或业务失败不是程序异常",
        "不作为异常控制流",
    ]:
        if text not in all_markdown:
            add_error(errors, f"缺少正常业务失败与程序异常边界规则：{text}")
    if "log.warn" in all_markdown and "不得空 catch、只写注释、只返回默认值或只使用 `log.warn`" not in all_markdown:
        add_error(errors, "异常处理规则不得使用 log.warn 作为消费异常的默认要求")

    forbidden_metric_patterns = [
        r"`active_connections`",
        r"`auth_fail_total`",
        r"`heartbeat_timeout_total`",
    ]
    for pattern in forbidden_metric_patterns:
        if re.search(pattern, all_markdown):
            add_error(errors, f"仍存在旧指标名称：{pattern}")

    for text in required_text:
        if text not in all_markdown:
            add_error(errors, f"缺少必需文本：{text}")


def validate_internal_sanity(errors: list[str]) -> None:
    legal_errors: list[str] = []
    validate_error_code_literals(
        "成功响应 code=000000；失败响应可返回 `AC0001`；模板格式为 `SMEEEE`。",
        legal_errors,
    )
    if legal_errors:
        add_error(errors, f"错误码格式自检误拦截合法样例：{legal_errors}")

    illegal_errors: list[str] = []
    validate_error_code_literals(
        '失败响应返回 `S00999`；不要写成 "code": "PARAM_ERROR" 或 "code": 100001。',
        illegal_errors,
    )
    for text in ["S00999", "PARAM_ERROR", "100001"]:
        if not any(text in error for error in illegal_errors):
            add_error(errors, f"错误码格式自检未能拦截非法样例 {text}")

    old_response_order_errors: list[str] = []
    validate_all_markdown_contracts(
        "旧响应字段顺序样例 code/message/data/ts",
        old_response_order_errors,
        ["旧响应字段顺序样例"],
    )
    if not any("code/message/data/ts" in error for error in old_response_order_errors):
        add_error(errors, "响应字段顺序自检未能拦截旧表述 code/message/data/ts")

    legal_fence_errors: list[str] = []
    validate_markdown_fences(
        "合法嵌套 fence 样例",
        "````markdown\n```text\nbody\n```\n````\n~~~text\nbody\n~~~",
        legal_fence_errors,
    )
    if legal_fence_errors:
        add_error(errors, f"Markdown fence 自检误拦截合法样例：{legal_fence_errors}")

    illegal_fence_errors: list[str] = []
    validate_markdown_fences("非法未闭合 fence 样例", "```text\nbody", illegal_fence_errors)
    if not illegal_fence_errors:
        add_error(errors, "Markdown fence 自检未能拦截未闭合代码块")

    placeholder_errors: list[str] = []
    validate_no_unresolved_placeholders("非法占位样例", "- ...\nservice/\n  XxxApplicationService.java", placeholder_errors)
    for text in ["省略号", "Xxx"]:
        if not any(text in error for error in placeholder_errors):
            add_error(errors, f"占位文本自检未能拦截非法样例 {text}")
