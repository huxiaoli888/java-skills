from __future__ import annotations

import re


def _add_error(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_implementation_plan_doc(
    implementation_text: str,
    errors: list[str],
    replay_key_text: tuple[str, ...],
    implementation_http_header_text: tuple[str, ...],
    implementation_signature_verifier_text: tuple[str, ...],
) -> None:
    if not implementation_text:
        return
    for text in ["Implementation Plan 模板", "TcpFrameDecoder", "TcpAuthHandler", "UdpDatagramDecoder", "SignatureVerifier", "ReplayKeyResolver", "ReplayCache", "MessageHandlerRegistry", "HttpHeaderSecurityFields", "MessageSecurityEnvelopeFields", "TcpUdpSecurityEnvelopeFields", "CanonicalBuilder"]:
        if text not in implementation_text:
            _add_error(errors, f"implementation-plan.md 缺少实现计划关键内容：{text}")
    tcp_auth_line = next((line for line in implementation_text.splitlines() if "`transport/tcp/TcpAuthHandler.java`" in line), "")
    for text in ["首条 `AUTH`", "认证窗口", "签名和重放校验", "普通业务 func 处理"]:
        if text not in tcp_auth_line:
            _add_error(errors, f"implementation-plan.md 的 TcpAuthHandler 职责不完整：{text}")
    envelope_line = next((line for line in implementation_text.splitlines() if "`protocol/MessageEnvelope.java`" in line), "")
    if "请求/通知 `reqid/func/version/ts/traceId/payload` envelope" not in envelope_line or "不作为响应 DTO" not in envelope_line:
        _add_error(errors, "implementation-plan.md 的 MessageEnvelope 职责必须收窄为请求/通知 envelope，不能作为响应 DTO")
    if "有序 UDP/TCP/WebSocket 业务可在 payload 内使用 `seqno`" not in envelope_line:
        _add_error(errors, "implementation-plan.md 的 MessageEnvelope 必须说明 UDP/TCP/WebSocket 有序业务可在 payload 内使用 seqno")
    for text in ["udid/authorization/sign/sign-alg/api-key"]:
        if text in envelope_line:
            _add_error(errors, f"implementation-plan.md 的 MessageEnvelope 不应承载 transport 专属安全字段：{text}")
    for text in ["transport 专属安全字段", "响应 JSON 字段"]:
        if text not in envelope_line:
            _add_error(errors, f"implementation-plan.md 的 MessageEnvelope 禁止承载列必须说明不承载：{text}")
    http_header_fields_line = next((line for line in implementation_text.splitlines() if "`protocol/HttpHeaderSecurityFields.java`" in line), "")
    if "HTTP/WebSocket Header 中" in http_header_fields_line:
        _add_error(errors, "implementation-plan.md 的 HttpHeaderSecurityFields 不应泛化为 HTTP/WebSocket Header，必须限定 WebSocket Upgrade")
    for text in implementation_http_header_text:
        if text not in http_header_fields_line:
            _add_error(errors, f"implementation-plan.md 的 HttpHeaderSecurityFields 职责不完整：{text}")
    message_security_fields_line = next((line for line in implementation_text.splitlines() if "`protocol/MessageSecurityEnvelopeFields.java`" in line), "")
    for text in ["WebSocket 首条 `AUTH`", "TCP `AUTH`", "TCP/UDP 高风险消息", "已认证 WebSocket 高风险业务消息", "sign/sign-alg/api-key", "`func` 风险等级或认证阶段", "消息级签名必填性", "HTTP Header 解析", "`udid` 或 `authorization` 主体解析"]:
        if text not in message_security_fields_line:
            _add_error(errors, f"implementation-plan.md 的 MessageSecurityEnvelopeFields 职责不完整：{text}")
    security_fields_line = next((line for line in implementation_text.splitlines() if "`protocol/TcpUdpSecurityEnvelopeFields.java`" in line), "")
    for text in ["udid/authorization", "匿名公开探测", "已识别设备请求", "高风险请求", "消息级 `sign/sign-alg/api-key` 交给 `MessageSecurityEnvelopeFields`", "WebSocket HTTP Header 解析", "已认证 WebSocket 业务消息字段解析"]:
        if text not in security_fields_line:
            _add_error(errors, f"implementation-plan.md 的 TcpUdpSecurityEnvelopeFields 职责不完整：{text}")
    replay_key_resolver_line = next((line for line in implementation_text.splitlines() if "`security/ReplayKeyResolver.java`" in line), "")
    for text in ["已解析安全字段", "signature-canonicalization.md", "防重放规则为准", "签名比较", "TTL 缓存存取", "业务幂等结果", "重新定义 replay key 形状"]:
        if text not in replay_key_resolver_line:
            _add_error(errors, f"implementation-plan.md 的 ReplayKeyResolver 职责边界缺少：{text}")
    for text in replay_key_text:
        if text in replay_key_resolver_line:
            _add_error(errors, f"implementation-plan.md 不应重复定义 replay key 形状，改引用 signature-canonicalization.md：{text}")
    replay_cache_line = next((line for line in implementation_text.splitlines() if "`security/ReplayCache.java`" in line), "")
    for text in ["接收 `ReplayKeyResolver` 输出", "短 TTL 去重", "脱敏传输响应摘要", "重放拒绝", "构造 replay key", "重拼 canonical string", "业务结果持久化"]:
        if text not in replay_cache_line:
            _add_error(errors, f"implementation-plan.md 的 ReplayCache 职责边界缺少：{text}")
    if "模糊连接身份去重" not in replay_cache_line:
        _add_error(errors, "implementation-plan.md 的 ReplayCache 禁止承载必须说明不能做模糊连接身份去重")
    for text in ["signature-canonicalization.md", "cluster-routing.md", "response-contract.md", "observability-testing.md"]:
        if text not in implementation_text:
            _add_error(errors, f"implementation-plan.md 必须提示按需读取：{text}")
    canonical_builder_line = next((line for line in implementation_text.splitlines() if "`security/canonical/*CanonicalBuilder.java`" in line), "")
    for text in ["HTTP", "WebSocket Upgrade", "WebSocket AUTH", "WebSocket 高风险业务消息", "TCP AUTH", "TCP/UDP 高风险消息", "CanonicalRequest", "UDID/KEY_ID/SIGN_ALG", "读取密钥", "比较签名"]:
        if text not in canonical_builder_line:
            _add_error(errors, f"implementation-plan.md 的 CanonicalBuilder 职责必须说明：{text}")
    auth_context_line = next((line for line in implementation_text.splitlines() if "`security/AuthContextResolver.java`" in line), "")
    for text in ["token", "短期票据", "设备凭据", "认证主体", "授权上下文", "WebSocket transport 生命周期", "具体业务规则"]:
        if text not in auth_context_line:
            _add_error(errors, f"implementation-plan.md 的 AuthContextResolver 职责必须说明：{text}")
    signature_verifier_line = next((line for line in implementation_text.splitlines() if "`security/SignatureVerifier.java`" in line), "")
    for text in implementation_signature_verifier_text:
        if text not in signature_verifier_line:
            _add_error(errors, f"implementation-plan.md 的 SignatureVerifier 职责必须说明：{text}")
    if "`writer/*ResponseWriter.java`" in implementation_text:
        _add_error(errors, "implementation-plan.md 不应使用通配 ResponseWriter，必须统一为 writer/NettyResponseWriter.java")
    netty_writer_line = next((line for line in implementation_text.splitlines() if "`writer/NettyResponseWriter.java`" in line), "")
    for text in ["统一响应", "ACK", "错误码映射", "日志脱敏", "reqid/code/message/ts/data", "禁止顶层 `func/version/traceId/status`", "协议专属分支膨胀"]:
        if text not in netty_writer_line:
            _add_error(errors, f"implementation-plan.md 的 NettyResponseWriter 职责必须说明：{text}")
    security_logger_line = next((line for line in implementation_text.splitlines() if "`observability/SecurityEventLogger.java`" in line), "")
    for text in ["鉴权、签名、重放和时间戳安全事件", "securityStage/signAlg/canonicalBuilder/contentTypeClass/bodyHashSource/replayKeyType", "GET query", "POST JSON raw body", "CMS form raw body", "body 原文", "body hash 原值"]:
        if text not in security_logger_line:
            _add_error(errors, f"implementation-plan.md 的 SecurityEventLogger 职责必须说明 HTTP/REST 签名观测边界：{text}")
    metrics_binder_line = next((line for line in implementation_text.splitlines() if "`observability/NettyMetricsBinder.java`" in line), "")
    for text in [
        "netty_signature_verify_total",
        "netty_signature_verify_duration_ms",
        "netty_signature_fail_total",
        "netty_replay_rejected_total",
        "netty_timestamp_skew_rejected_total",
        "transport/nodeId/stage/reason/signAlg/canonicalBuilder/bodyHashSource/contentTypeClass",
        "正常验签耗时标签只用有限枚举",
        "高基数字段",
    ]:
        if text not in metrics_binder_line:
            _add_error(errors, f"implementation-plan.md 的 NettyMetricsBinder 职责必须说明安全指标标签边界：{text}")
    for text in [
        "HTTP/REST 必须覆盖 GET query 排序",
        "POST `application/json` 原始 body hash",
        "CMS POST `application/x-www-form-urlencoded` 原始表单 body hash",
        "`canonicalBuilder/bodyHashSource/contentTypeClass` 日志字段",
        "`netty_signature_verify_total`",
        "`netty_signature_verify_duration_ms`",
        "`netty_signature_fail_total` 标签",
    ]:
        if text not in implementation_text:
            _add_error(errors, f"implementation-plan.md 的安全测试计划必须覆盖 HTTP/REST body/query 签名证据：{text}")


def validate_implementation_layout_doc(layout_text: str, errors: list[str], replay_key_text: tuple[str, ...]) -> None:
    if not layout_text:
        return
    if "WsResponseWriter.java" in layout_text or "TcpResponseWriter" in layout_text or "UdpResponseWriter" in layout_text:
        _add_error(errors, "implementation-layout.md 不应在 transport 层放协议专属 ResponseWriter")
    if "WsAuthService.java" in layout_text:
        _add_error(errors, "implementation-layout.md 不应把 WebSocket 鉴权 service 放在 transport/websocket 下")
    if "writer/\n  NettyResponseWriter.java" not in layout_text:
        _add_error(errors, "implementation-layout.md 必须在 writer 层保留 NettyResponseWriter.java")
    if "`writer/*` 统一响应" in layout_text:
        _add_error(errors, "implementation-layout.md 不应使用 writer/* 通配职责，必须点名 NettyResponseWriter.java")
    if "ProtocolErrorCode.java" in layout_text:
        _add_error(errors, "implementation-layout.md 不应在 protocol 层建议 ProtocolErrorCode.java，错误码映射归 writer/NettyResponseWriter.java")
    protocol_responsibility_line = next((line for line in layout_text.splitlines() if "`protocol/*`" in line), "")
    for text in ["字段解析", "字段校验", "解析结果", "不做响应 JSON 或错误码映射", "类型化失败原因"]:
        if text not in protocol_responsibility_line:
            _add_error(errors, f"implementation-layout.md 的 protocol 层职责必须保持解析边界：{text}")
    if "错误码和解析结果" in protocol_responsibility_line:
        _add_error(errors, "implementation-layout.md 的 protocol 层不应声明处理错误码，错误码映射归 NettyResponseWriter")
    if "不按 UDP/TCP/WebSocket 拆协议专属 writer" not in layout_text:
        _add_error(errors, "implementation-layout.md 必须说明不按协议拆分 ResponseWriter")
    for text in ["writer/NettyResponseWriter.java` 按 `response-contract.md` 统一响应 JSON、ACK、错误码映射和日志脱敏", "响应和 ACK 只写 `reqid/code/message/ts/data`", "禁止顶层 `func/version/traceId/status`"]:
        if text not in layout_text:
            _add_error(errors, f"implementation-layout.md 的 NettyResponseWriter 职责必须说明：{text}")
    for text in ["transport/", "websocket/", "tcp/", "udp/", "TcpFrameDecoder.java", "TcpAuthHandler.java", "UdpDatagramDecoder.java", "HttpHeaderSecurityFields.java", "MessageSecurityEnvelopeFields.java", "TcpUdpSecurityEnvelopeFields.java", "SignatureVerifier.java", "ReplayKeyResolver.java", "ReplayCache.java"]:
        if text not in layout_text:
            _add_error(errors, f"implementation-layout.md 缺少通用落地结构关键内容：{text}")
    for text in [
        "`protocol/MessageSecurityEnvelopeFields.java` 只解析 WebSocket 首条 `AUTH`、TCP `AUTH`、TCP/UDP 高风险消息和已认证 WebSocket 高风险业务消息 envelope 顶层 `sign/sign-alg/api-key`",
        "不解析 HTTP Header、`udid`、`authorization` 或主体身份",
        "`protocol/TcpUdpSecurityEnvelopeFields.java` 只解析 TCP/UDP envelope 顶层 `udid/authorization`",
        "不承载已认证 WebSocket 业务消息字段",
    ]:
        if text not in layout_text:
            _add_error(errors, f"implementation-layout.md 必须说明消息级安全字段边界：{text}")
    for text in [
        "canonical/",
        "CanonicalRequest.java",
        "HttpRequestCanonicalBuilder.java",
        "WebSocketUpgradeCanonicalBuilder.java",
        "WebSocketAuthCanonicalBuilder.java",
        "WebSocketMessageCanonicalBuilder.java",
        "TcpAuthCanonicalBuilder.java",
        "TcpUdpMessageCanonicalBuilder.java",
        "AuthContextResolver.java",
        "ReplayKeyResolver.java",
        "`security/canonical/*` 只做不同入口的 canonical request 构造，不读取密钥、不比较签名",
        "`CanonicalRequest.java` 必须显式承载 `UDID/KEY_ID/SIGN_ALG` 槽位",
        "`security/AuthContextResolver.java` 只做 token、短期票据或设备凭据到认证主体的解析与上下文构造",
    ]:
        if text not in layout_text:
            _add_error(errors, f"implementation-layout.md 必须包含 canonical builder 落地结构或边界：{text}")
    replay_key_resolver_layout_line = next((line for line in layout_text.splitlines() if "`security/ReplayKeyResolver.java`" in line), "")
    for text in ["已解析安全字段", "signature-canonicalization.md", "防重放规则为准", "不做 TTL 缓存存取", "业务幂等结果保存", "重新定义 replay key 形状"]:
        if text not in replay_key_resolver_layout_line:
            _add_error(errors, f"implementation-layout.md 的 ReplayKeyResolver 职责边界缺少：{text}")
    for text in replay_key_text:
        if text in replay_key_resolver_layout_line:
            _add_error(errors, f"implementation-layout.md 不应重复定义 replay key 形状，改引用 signature-canonicalization.md：{text}")
    replay_cache_layout_line = next((line for line in layout_text.splitlines() if "`security/ReplayCache.java`" in line), "")
    for text in ["`ReplayKeyResolver` 输出", "短 TTL 去重", "脱敏传输响应摘要", "不重拼 canonical string", "不构造 replay key", "不保存业务幂等结果", "不做模糊连接身份去重"]:
        if text not in replay_cache_layout_line:
            _add_error(errors, f"implementation-layout.md 的 ReplayCache 职责边界缺少：{text}")
    for text in ["observability/", "SecurityEventLogger.java", "NettyMetricsBinder.java"]:
        if text not in layout_text:
            _add_error(errors, f"implementation-layout.md 必须包含 observability 落地结构：{text}")
    security_logger_layout_line = next((line for line in layout_text.splitlines() if "`observability/SecurityEventLogger.java`" in line), "")
    for text in ["securityStage/signAlg/canonicalBuilder/contentTypeClass/bodyHashSource/replayKeyType", "不记录完整签名", "完整 `Content-Type`", "body 原文", "body hash 原值"]:
        if text not in security_logger_layout_line:
            _add_error(errors, f"implementation-layout.md 的 SecurityEventLogger 职责边界缺少：{text}")
    metrics_binder_layout_line = next((line for line in layout_text.splitlines() if "`observability/NettyMetricsBinder.java`" in line), "")
    for text in ["netty_*", "transport/nodeId/stage/reason/signAlg/canonicalBuilder/bodyHashSource/contentTypeClass", "不使用 `reqid/connectionId/userId/udid/IP/bodyHash`"]:
        if text not in metrics_binder_layout_line:
            _add_error(errors, f"implementation-layout.md 的 NettyMetricsBinder 职责边界缺少：{text}")
    for text in ["handler/", "  MessageHandler.java", "  V2TokenUploadHandler.java", "  DeviceStatusReportHandler.java"]:
        if text not in layout_text:
            _add_error(errors, f"implementation-layout.md 必须包含 handler 落地结构：{text}")
    if "router/\n  MessageHandler.java" in layout_text:
        _add_error(errors, "implementation-layout.md 不应把 MessageHandler.java 放在 router/ 目录下")
    if "`router/*` 只做 `func + version` 到 handler 的显式注册和查找，不承载具体业务 handler" not in layout_text:
        _add_error(errors, "implementation-layout.md 必须说明 router 不承载具体业务 handler")
    if "public class MessageHandlerRegistry" not in layout_text:
        _add_error(errors, "implementation-layout.md 必须承载通用 MessageHandlerRegistry 示例")
    if 'throw new ProtocolException("AC0002")' in layout_text:
        _add_error(errors, "implementation-layout.md 的 Registry 示例不应硬编码响应错误码，应该抛类型化异常交给 NettyResponseWriter 映射")
    if "UnsupportedMessageHandlerException(key)" not in layout_text:
        _add_error(errors, "implementation-layout.md 的 Registry 示例应使用类型化 UnsupportedMessageHandlerException 表达未知 func/version")
