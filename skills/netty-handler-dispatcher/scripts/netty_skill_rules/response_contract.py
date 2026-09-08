from __future__ import annotations

import re


ERROR_CODE_PATTERN = re.compile(r"^(000000|[A-Z]{2}\d{4})$")


def _add_error(errors: list[str], message: str) -> None:
    errors.append(message)


def _quoted_code_literals(text: str) -> list[str]:
    return sorted(set(re.findall(r'"((?=[A-Za-z0-9]*\d)[A-Za-z0-9]{5,6})"', text)))


def validate_protocol_response_boundary_doc(protocol_text: str, errors: list[str]) -> None:
    for text in ["成功响应：", "错误响应：", "ACK：", "限流响应示例："]:
        if text in protocol_text:
            _add_error(errors, f"protocol-format.md 不应维护完整响应/ACK 示例，改引用 response-contract.md：{text}")
    if "响应与 ACK 的完整 JSON 示例、字段语义、错误码格式和 ACK `data.ackFunc/data.ackStatus` 规则见 `response-contract.md`" not in protocol_text:
        _add_error(errors, "protocol-format.md 必须说明响应/ACK 完整示例归 response-contract.md")
    if "限流、服务繁忙、鉴权失败等响应体示例不要在本文件维护" not in protocol_text:
        _add_error(errors, "protocol-format.md 必须禁止在协议格式文档维护具体错误响应体示例")
    error_code_section = re.search(r"## 错误码规则(?P<body>[\s\S]*?)(?:\n## |\Z)", protocol_text)
    error_code_text = error_code_section.group("body") if error_code_section else ""
    for text in [
        "完整响应 JSON、ACK 和错误码契约以 `response-contract.md` 为准",
        "本节只记录协议层必须遵守的摘要边界",
        "成功固定为 `000000`",
        "失败使用 `SMEEEE` 格式稳定错误码",
        "HTTP、UDP、TCP、WebSocket 四类入口含义一致",
        "只允许 `reqid/code/message/ts/data`",
        "具体 `reqid` 回传",
    ]:
        if text not in error_code_text:
            _add_error(errors, f"protocol-format.md 的错误码章节必须引用 response-contract 并只保留摘要：{text}")
    for text in ["`S`：", "`M`：", "`EEEE`：", "参数错误", "功能或版本不支持", "未鉴权", "请求过于频繁"]:
        if text in error_code_text:
            _add_error(errors, f"protocol-format.md 的错误码章节不应重复 response-contract 详细规则：{text}")


def validate_response_contract_doc(response_text: str, errors: list[str]) -> None:
    if not response_text:
        return
    for text in ["reqid", "code", "message", "data", "ts", "SMEEEE", "000000"]:
        if text not in response_text:
            _add_error(errors, f"response-contract.md 缺少响应契约关键内容：{text}")
    for text in [
        "`S`：1 位大写字母",
        "`M`：1 位大写字母",
        "`EEEE`：4 位数字",
        "失败 `code` 使用 6 位字符串",
    ]:
        if text not in response_text:
            _add_error(errors, f"response-contract.md 缺少错误码格式定义：{text}")
    for code in _quoted_code_literals(response_text):
        if not ERROR_CODE_PATTERN.match(code):
            _add_error(errors, f"response-contract.md 示例错误码格式非法：{code}，必须是 000000 或 2 位大写字母 + 4 位数字")
    for text in [
        "ACK 属于响应类消息",
        "data.ackFunc",
        "data.ackStatus",
        "不返回顶层 `func`、`version`、`traceId` 或 `status`",
        "禁止的是响应或 ACK 顶层协议状态字段",
        "业务 `payload` 或 `data` 里的订单状态、设备状态、令牌状态等领域字段可以存在",
        "机器枚举值放在 `data.ackStatus`",
        "ACK 不作为入站业务 `func + version` 注册 handler",
    ]:
        if text not in response_text:
            _add_error(errors, f"response-contract.md 缺少 ACK 响应契约：{text}")
    if '"message": "RECEIVED"' in response_text:
        _add_error(errors, "response-contract.md 的 ACK 示例 message 应使用中文提示，机器枚举值放在 ackStatus")
    if "数字字符串" in response_text:
        _add_error(errors, "response-contract.md 不应把 SMEEEE 错误码描述为数字字符串")
