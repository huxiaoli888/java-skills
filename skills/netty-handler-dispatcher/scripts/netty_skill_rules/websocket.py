from __future__ import annotations

import re


def _add_error(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_websocket_doc(websocket_text: str, errors: list[str], websocket_http_rest_boundary_text: tuple[str, ...]) -> None:
    if not websocket_text:
        return

    if re.search(r"\bAC000\d\b", websocket_text):
        _add_error(errors, "netty-websocket.md 不应直接定义 AC000x，transport 只产生类型化失败，code 由 NettyResponseWriter 按 response-contract.md 映射")
    for text in ["本文件不定义具体 `AC000x` 错误码", "WebSocket transport 只产生类型化失败原因", "writer/NettyResponseWriter.java", "response-contract.md"]:
        if text not in websocket_text:
            _add_error(errors, f"netty-websocket.md 必须说明 transport 错误码归属边界：{text}")
    if "WsResponseWriter" in websocket_text:
        _add_error(errors, "netty-websocket.md 不应把响应写回器放在 WebSocket transport 专项类中")
    if "writer/NettyResponseWriter.java" not in websocket_text:
        _add_error(errors, "netty-websocket.md 必须指向统一 writer/NettyResponseWriter.java")
    upgrade_line = next((line for line in websocket_text.splitlines() if "HttpUpgradeAuthHandler" in line and "Upgrade 前校验" in line), "")
    if "x-api-key" not in upgrade_line:
        _add_error(errors, "netty-websocket.md 的 HttpUpgradeAuthHandler 说明必须包含 x-api-key")
    lifecycle_line = next((line for line in websocket_text.splitlines() if "校验 authorization" in line), "")
    if "x-api-key" not in lifecycle_line or "appKey/keyId" in lifecycle_line:
        _add_error(errors, "netty-websocket.md 的鉴权生命周期主流程必须使用 x-api-key，不应推荐 appKey/keyId")
    for text in websocket_http_rest_boundary_text:
        if text not in websocket_text:
            _add_error(errors, f"netty-websocket.md 必须澄清 WebSocket x-api-key 与 CMS HTTP/REST 公参边界：{text}")
    if "WebSocket 落地边界" not in websocket_text or "implementation-layout.md" not in websocket_text:
        _add_error(errors, "netty-websocket.md 必须只描述 WebSocket 落地边界并指向 implementation-layout.md")
    if "public class MessageHandlerRegistry" in websocket_text:
        _add_error(errors, "netty-websocket.md 不应承载通用 MessageHandlerRegistry 示例")
    for text in ["WebSocket 有顺序语义的业务可在 `payload.seqno`", "`seqno` 不替代 `reqid`", "不进入通用 envelope 顶层"]:
        if text not in websocket_text:
            _add_error(errors, f"netty-websocket.md 必须说明 WebSocket 业务顺序字段边界：{text}")
    auth_message_example = re.search(r"`auth-message` 首条 `AUTH` 示例：[\s\S]*?```json\n(?P<body>[\s\S]*?)\n```", websocket_text)
    if not auth_message_example:
        _add_error(errors, "netty-websocket.md 必须提供 auth-message 首条 AUTH 示例")
    else:
        auth_body = auth_message_example.group("body")
        for text in ['"func": "AUTH"', '"authorization": "Bearer token"', '"sign": "signature"', '"sign-alg": "HMAC-SHA256"', '"api-key": "key-id"']:
            if text not in auth_body:
                _add_error(errors, f"netty-websocket.md 的 AUTH 示例缺少字段：{text}")
        for text in ['"x-reqid"', '"x-timestamp"', '"x-api-version"']:
            if text in auth_body:
                _add_error(errors, f"netty-websocket.md 的 AUTH 示例不应在消息体中重复 HTTP Header 字段：{text}")
    for text in ["signed-upgrade:", "auth-message:", "hybrid:", "BODY_SHA256_HEX", "canonical payload bytes"]:
        if text not in websocket_text:
            _add_error(errors, f"netty-websocket.md 必须说明 auth.mode 分支或 AUTH 签名原文：{text}")
    auth_message_flow = re.search(r"auth-message:\n(?P<body>[\s\S]*?)\n\nhybrid:", websocket_text)
    if not auth_message_flow:
        _add_error(errors, "netty-websocket.md 必须在鉴权流程中明确 auth-message 分支")
    else:
        for text in [
            "reqid / ts / version / func / authorization / sign / sign-alg / api-key",
            "WebSocketAuthCanonicalBuilder",
            "ws-auth replay key",
        ]:
            if text not in auth_message_flow.group("body"):
                _add_error(errors, f"netty-websocket.md 的 auth-message 流程必须说明 AUTH envelope/canonical/replay 边界：{text}")
    auth_message_rule_line = next((line for line in websocket_text.splitlines() if "`auth-message` 模式下" in line), "")
    for text in ["WebSocketAuthCanonicalBuilder", "reqid/ts/api-key/sign-alg/version/func", "原始消息体 bytes"]:
        if text not in auth_message_rule_line:
            _add_error(errors, f"netty-websocket.md 的 auth-message 规则必须对齐 signature-canonicalization：{text}")
    for text in ["ws-upgrade:{x-api-key}:{x-reqid}:{authSubject|clientId}", "ws-auth:{api-key}:{reqid}:{ticketId|authSubject|connectionId}", "ws-message:{api-key}:{reqid}:{authSubject|connectionId}", "票据必须单次使用", "不能只校验时间戳或只依赖 `connectionId`"]:
        if text not in websocket_text:
            _add_error(errors, f"netty-websocket.md 的防重放维度缺少：{text}")
    for text in [
        "security:",
        "timestamp-skew-seconds: 300",
        "replay-ttl-seconds: 300",
        "`security.timestamp-skew-seconds` 控制 WebSocket Upgrade Header `x-timestamp` 或消息 envelope `ts`",
        "`security.replay-ttl-seconds` 控制 `ws-upgrade/ws-auth/ws-message` replay key",
        "认证超时只限制连接阶段，不能替代签名防重放窗口",
        "已设置签名时间戳偏差窗口和 `ws-upgrade/ws-auth/ws-message` 防重放 TTL",
    ]:
        if text not in websocket_text:
            _add_error(errors, f"netty-websocket.md 的基础配置模板必须覆盖 WebSocket 防重放窗口：{text}")
    websocket_high_risk_example = re.search(r"已认证 WebSocket 高风险业务消息示例：[\s\S]*?```json\n(?P<body>[\s\S]*?)\n```", websocket_text)
    if not websocket_high_risk_example:
        _add_error(errors, "netty-websocket.md 必须提供已认证 WebSocket 高风险业务消息示例")
    else:
        high_risk_ws_body = websocket_high_risk_example.group("body")
        for text in ['"func": "TOKEN_UPLOAD"', '"sign": "signature"', '"sign-alg": "HMAC-SHA256"', '"api-key": "key-id"']:
            if text not in high_risk_ws_body:
                _add_error(errors, f"netty-websocket.md 的已认证高风险业务消息示例缺少字段：{text}")
        for text in ['"x-reqid"', '"x-timestamp"', '"x-sign"', '"x-sign-alg"', '"x-api-version"', '"x-api-key"']:
            if text in high_risk_ws_body:
                _add_error(errors, f"netty-websocket.md 的已认证高风险业务消息示例不应携带 HTTP Header 字段：{text}")
    for text in [
        "`WsMessageDispatcher` 在分发已认证业务消息前",
        "`protocol/MessageSecurityEnvelopeFields.java`",
        "高风险业务消息必须在 envelope 顶层携带 `sign/sign-alg/api-key`",
        "高风险业务消息的 `reqid` 在 replay window 内唯一",
        "`ws-message:{api-key}:{reqid}:{authSubject|connectionId}`",
        "不要把 HTTP `x-reqid/x-timestamp/x-sign/x-sign-alg/x-api-version/x-api-key` 放入 `payload`",
        "`UDID` 槽位使用空字符串",
        "不要塞进 `WsAuthMessageHandler` 或 `WsMessageDispatcher` 的业务分支",
    ]:
        if text not in websocket_text:
            _add_error(errors, f"netty-websocket.md 必须覆盖已认证高风险消息级签名边界：{text}")
