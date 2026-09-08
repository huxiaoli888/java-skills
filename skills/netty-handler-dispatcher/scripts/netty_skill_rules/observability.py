from __future__ import annotations

import re


def _add_error(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_observability_testing_doc(observability_text: str, errors: list[str]) -> None:
    if not observability_text:
        return
    if "旧 UDP/TCP/HTTP 入口与新 Netty UDP/TCP/WebSocket 入口业务结果一致" not in observability_text:
        _add_error(errors, "observability-testing.md 的兼容测试必须覆盖 UDP/TCP/HTTP 和 Netty UDP/TCP/WebSocket")
    for old_label in ["`transport`, `nodeId`, `appKey`", "`transport`, `nodeId`, `apiKey`"]:
        if old_label in observability_text:
            _add_error(errors, "observability-testing.md 的连接数指标不应使用 appKey/apiKey，统一使用低基数 apiKeyGroup")
    if "`transport`, `nodeId`, `apiKeyGroup`" not in observability_text:
        _add_error(errors, "observability-testing.md 的连接数指标应使用 apiKeyGroup 标签")
    if "`udid/userId/deviceId/clientId`" not in observability_text:
        _add_error(errors, "observability-testing.md 的结构化日志主体字段必须包含 udid")
    for text in [
        "`securityStage`",
        "`signAlg`",
        "`canonicalBuilder`",
        "`contentTypeClass`",
        "`bodyHashSource`",
        "`replayKeyType`",
        "不要记录完整 replay key",
    ]:
        if text not in observability_text:
            _add_error(errors, f"observability-testing.md 必须覆盖安全事件日志字段：{text}")
    for text in [
        "`connectionId` | TCP/WebSocket 连接 ID；UDP 无稳定连接时为空",
        "`routeId` | UDP 上层 session 或异步响应 route ID；TCP/WebSocket 可为空",
        "`netty_udp_routes_active`",
        "`netty_udp_routes_created_total`",
        "`netty_udp_routes_expired_total`",
        "`netty_connections_*` 只表达 TCP/WebSocket 连接",
        "UDP 不应伪造连接数",
        "UDP route 数、route 创建/过期速率、datagram 丢弃原因",
        "UDP 稳定性：datagram 丢弃率、乱序/重复率、route 过期率和固定入口节点切换恢复",
    ]:
        if text not in observability_text:
            _add_error(errors, f"observability-testing.md 必须覆盖 UDP route 观测边界：{text}")
    for text in [
        "`netty_signature_fail_total`",
        "`netty_signature_verify_total`",
        "`netty_signature_verify_duration_ms`",
        "`netty_replay_rejected_total`",
        "`netty_timestamp_skew_rejected_total`",
        "| `netty_message_latency_ms` | Histogram | `transport`, `nodeId`, `func`, `version`, `code` |",
        "| `netty_message_errors_total` | Counter | `transport`, `nodeId`, `func`, `version`, `code` |",
        "| `netty_ack_timeout_total` | Counter | `transport`, `nodeId`, `func`, `version` |",
        "| `netty_rate_limited_total` | Counter | `transport`, `nodeId`, `dimension`, `func` |",
        "`apiKeyGroup` 标签只能使用低基数的公开密钥分组、租户分组或 `public/unknown`",
        "不得使用请求里的 `x-api-key/api-key` 原值、HMAC secret、私钥、token、完整 credential、手机号、`udid` 或高基数动态值",
        "`transport`, `nodeId`, `stage`, `reason`, `signAlg`, `canonicalBuilder`, `bodyHashSource`, `contentTypeClass`",
        "`transport`, `nodeId`, `stage`, `result`, `signAlg`, `canonicalBuilder`",
        "`transport`, `nodeId`, `stage`, `replayKeyType`, `reason`",
        "`transport`, `nodeId`, `stage`, `reason`",
        "`nodeId` 用于多实例定位，核心消息延迟、错误、ACK 超时、限流和安全失败指标都应携带",
        "`stage`、`reason`、`signAlg`、`replayKeyType`、`canonicalBuilder`、`bodyHashSource`、`contentTypeClass` 必须是有限枚举",
        "`result` 只能使用 `success/fail/skipped` 这类有限枚举",
        "用于评估正常请求的 HMAC 成本和算法退化",
        "不要把完整签名、完整 replay key、token、`api-key` 原值、完整 `Content-Type`、body 原文、body hash 原值或 `udid` 放进 metrics 标签",
        "签名失败突增",
        "重放拦截突增",
        "时间戳偏差拒绝突增",
        "签名错误、时间戳超窗",
        "`netty_signature_fail_total`、`netty_replay_rejected_total`、`netty_timestamp_skew_rejected_total` 递增",
        "安全失败事件不会进入业务 handler",
    ]:
        if text not in observability_text:
            _add_error(errors, f"observability-testing.md 必须覆盖签名/重放/时间戳安全观测：{text}")
    for text in [
        "HTTP/REST 覆盖 GET query 排序",
        "POST `application/json` 原始 body hash",
        "CMS POST `application/x-www-form-urlencoded` 原始表单 body hash",
        "`canonicalBuilder/bodyHashSource/contentTypeClass` 日志字段",
    ]:
        if text not in observability_text:
            _add_error(errors, f"observability-testing.md 的安全测试必须覆盖 HTTP/REST body/query 签名排查证据：{text}")
    for text in [
        "出站响应和 ACK 指标的 `func/version` 标签必须来自入站请求/通知上下文或 `data.ackFunc` 对应的协议上下文",
        "不能为了打指标把 `func/version/traceId/status` 放回响应 JSON 顶层",
    ]:
        if text not in observability_text:
            _add_error(errors, f"observability-testing.md 必须说明出站指标标签不改变响应契约：{text}")
    if "UDP source address" in observability_text and "稳定连接" in observability_text:
        _add_error(errors, "observability-testing.md 不应把 UDP source address 描述为稳定连接")
