"""protocol-format.md contract checks for the Netty skill."""

from __future__ import annotations

import re

from netty_skill_rules import response_contract, security


def add_error(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_protocol_format_doc(protocol_text: str, errors: list[str]) -> None:
    if not protocol_text:
        return
    response_contract.validate_protocol_response_boundary_doc(protocol_text, errors)
    if "HEARTBEAT" not in protocol_text or "ACK" not in protocol_text:
        add_error(errors, "protocol-format.md 必须说明 HEARTBEAT/ACK 的签名处理")
    if "signature-canonicalization.md" not in protocol_text:
        add_error(errors, "protocol-format.md 必须引用 signature-canonicalization.md 作为签名原文和防重放规则来源")
    if '"udid": "optional-device-or-user-id"' in protocol_text or "TCP/UDP 请求可选设备或用户唯一标识" in protocol_text:
        add_error(errors, "protocol-format.md 不应把所有 TCP/UDP udid 一概描述为可选字段；只能允许匿名公开探测省略")
    if "`sequence`、" in protocol_text:
        add_error(errors, "protocol-format.md 不应继续使用 sequence 示例，统一使用 seqno")
    if '"func": "TOKEN_UPLOAD"' in protocol_text:
        for text in ['"authorization": "optional-token"', '"sign": "optional-signature"', '"sign-alg": "optional-algorithm"', '"api-key": "optional-key-id"']:
            if text in protocol_text:
                add_error(errors, f"protocol-format.md 的 TOKEN_UPLOAD 高风险示例不应使用 optional 安全字段：{text}")
        if "`TOKEN_UPLOAD` 属于高风险业务示例" not in protocol_text or "TCP/UDP 示例必须携带 `udid/authorization/sign/sign-alg/api-key`" not in protocol_text:
            add_error(errors, "protocol-format.md 必须说明 TOKEN_UPLOAD 示例属于高风险业务且 TCP/UDP 安全字段必填")
    tcp_udp_request_block = re.search(r"TCP/UDP 高风险请求：[\s\S]*?```json\n(?P<body>[\s\S]*?)\n```", protocol_text)
    if not tcp_udp_request_block:
        add_error(errors, "protocol-format.md 必须拆出 TCP/UDP 高风险请求示例")
    else:
        for text in ['"udid": "device-or-user-id"', '"authorization": "Bearer token"', '"sign": "signature"', '"sign-alg": "HMAC-SHA256"', '"api-key": "key-id"']:
            if text not in tcp_udp_request_block.group("body"):
                add_error(errors, f"protocol-format.md 的 TCP/UDP 高风险请求示例缺少字段：{text}")
    websocket_low_risk_block = re.search(r"WebSocket 已认证连接上的低风险业务请求：[\s\S]*?```json\n(?P<body>[\s\S]*?)\n```", protocol_text)
    if not websocket_low_risk_block:
        add_error(errors, "protocol-format.md 必须拆出 WebSocket 已认证低风险业务请求示例")
    else:
        for text in ['"udid"', '"authorization"', '"sign"', '"sign-alg"', '"api-key"']:
            if text in websocket_low_risk_block.group("body"):
                add_error(errors, f"protocol-format.md 的 WebSocket 低风险业务请求示例不应携带 TCP/UDP 或消息级安全字段：{text}")
    websocket_high_risk_block = re.search(r"WebSocket 已认证连接上的高风险业务请求：[\s\S]*?```json\n(?P<body>[\s\S]*?)\n```", protocol_text)
    if not websocket_high_risk_block:
        add_error(errors, "protocol-format.md 必须拆出 WebSocket 已认证高风险业务请求示例")
    else:
        high_risk_body = websocket_high_risk_block.group("body")
        for text in ['"func": "TOKEN_UPLOAD"', '"sign": "signature"', '"sign-alg": "HMAC-SHA256"', '"api-key": "key-id"']:
            if text not in high_risk_body:
                add_error(errors, f"protocol-format.md 的 WebSocket 高风险业务请求示例缺少消息级签名字段：{text}")
        for text in ['"udid"', '"authorization"', '"x-reqid"', '"x-timestamp"', '"x-api-version"']:
            if text in high_risk_body:
                add_error(errors, f"protocol-format.md 的 WebSocket 高风险业务请求示例不应携带该字段：{text}")
    for text in ["WebSocket 的握手签名使用 HTTP Header", "握手后的低风险业务消息可依赖已认证连接", "高风险业务消息必须按消息级签名规则", "不要把 HTTP `x-*` Header 字段放入 `payload`"]:
        if text not in protocol_text:
            add_error(errors, f"protocol-format.md 缺少 WebSocket 与 TCP/UDP 安全字段边界说明：{text}")
    if "`HEARTBEAT`、`ACK`、低风险服务端通知可依赖已认证连接" in protocol_text:
        add_error(errors, "protocol-format.md 不应泛化说低风险消息可依赖已认证连接，必须限定 TCP/WebSocket")
    if "连接认证、`reqid` 和业务顺序字段 `seqno`" in protocol_text:
        add_error(errors, "protocol-format.md 不应暗示低风险消息都必须携带 seqno")
    for text in [
        "TCP/WebSocket 已认证连接上的 `HEARTBEAT`",
        "可依赖连接认证和 `reqid`",
        "只有具备业务顺序语义的消息才在 `payload.seqno` 中使用顺序号",
        "`seqno` 不替代 `reqid` 或 replay key",
        "UDP 没有可靠连接态",
        "UDP 高风险请求仍必须逐条携带鉴权和签名材料",
    ]:
        if text not in protocol_text:
            add_error(errors, f"protocol-format.md 的消息级签名豁免边界缺少：{text}")
    for field in ["`sign`", "`sign-alg`", "`api-key`"]:
        field_line = next((line for line in protocol_text.splitlines() if line.startswith(f"| {field} |")), "")
        for text in ["TCP/UDP 高风险必填", "WebSocket 高风险业务消息级签名必填，低风险可省略"]:
            if text not in field_line:
                add_error(errors, f"protocol-format.md 的 {field} 字段必填性必须区分 TCP/UDP 与 WebSocket 高低风险：{text}")
    extension_block = re.search(
        r"可选扩展字段：[\s\S]*?```json\n(?P<body>[\s\S]*?)\n```",
        protocol_text,
    )
    if extension_block and '"func": "TOKEN_UPLOAD"' in extension_block.group("body"):
        add_error(errors, "protocol-format.md 的可选扩展字段示例不应使用高风险 TOKEN_UPLOAD")
    for field in ["`code`", "`message`", "`data`"]:
        ack_optional_pattern = rf"\| {re.escape(field)} \| 禁止 \| 必填 \| 禁止 \| 可选 \|"
        if re.search(ack_optional_pattern, protocol_text):
            add_error(errors, f"protocol-format.md 的 ACK 字段 {field} 不应标为可选")
    if '"message": "RECEIVED"' in protocol_text:
        add_error(errors, "protocol-format.md 的 ACK 示例 message 应使用中文提示，机器枚举值放在 ackStatus")
    if "转换成数字字符串" in protocol_text:
        add_error(errors, "protocol-format.md 不应把 SMEEEE 错误码描述为数字字符串")
    security.validate_protocol_signature_replay_doc(protocol_text, errors)

