from __future__ import annotations

import re


def _add_error(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_signature_canonicalization_doc(signature_text: str, errors: list[str], replay_key_text: tuple[str, ...]) -> None:
    if not signature_text:
        return
    if "# 长连接签名 Canonicalization 规则" in signature_text:
        _add_error(errors, "signature-canonicalization.md 标题不应只描述为长连接签名")
    if "# Netty 传输签名 Canonicalization 规则" not in signature_text:
        _add_error(errors, "signature-canonicalization.md 标题必须覆盖 Netty 传输签名")
    if "长连接中高风险业务 `func`" in signature_text:
        _add_error(errors, "signature-canonicalization.md 不应把高风险业务消息级签名只描述为长连接场景")
    if "`HEARTBEAT`、`ACK`、低风险服务端通知可以依赖已认证连接" in signature_text:
        _add_error(errors, "signature-canonicalization.md 不应泛化说低风险消息可依赖已认证连接，必须限定 TCP/WebSocket")
    if "连接认证、`reqid` 和业务顺序字段 `seqno`" in signature_text:
        _add_error(errors, "signature-canonicalization.md 不应暗示低风险消息都必须携带 seqno")
    for text in [
        "TCP/WebSocket 已认证连接上的 `HEARTBEAT`",
        "可以依赖连接认证和 `reqid`",
        "只有具备业务顺序语义的消息才在 `payload.seqno` 中使用顺序号",
        "`seqno` 不替代 `reqid` 或 replay key",
        "UDP 没有可靠连接态",
        "匿名公开低风险 UDP 探测只能依赖限流和风控",
    ]:
        if text not in signature_text:
            _add_error(errors, f"signature-canonicalization.md 的消息级签名豁免边界缺少：{text}")
    canonical_block = re.search(r"```text\nMETHOD\n[\s\S]*?BODY_SHA256_HEX\n```", signature_text)
    if not canonical_block or "UDID" not in canonical_block.group(0):
        _add_error(errors, "signature-canonicalization.md 的签名原文必须包含 UDID")
    if not canonical_block or "SIGN_ALG" not in canonical_block.group(0):
        _add_error(errors, "signature-canonicalization.md 的签名原文必须包含 SIGN_ALG，防止算法标识未绑定进签名")
    for text in ["`SIGN_ALG` 使用 `x-sign-alg` 或 envelope `sign-alg` 的原始字符串", "防止算法标识被替换"]:
        if text not in signature_text:
            _add_error(errors, f"signature-canonicalization.md 必须说明签名算法槽位边界：{text}")
    if "reqid/sequence" in signature_text:
        _add_error(errors, "signature-canonicalization.md 不应继续使用 reqid/sequence，统一使用 reqid/seqno")
    if re.search(r"(?m)^v\d+$", signature_text):
        _add_error(errors, "signature-canonicalization.md 的 canonical 示例版本行必须使用 V1/V2 这类大写稳定字符串")
    if "TCP/UDP 高风险业务消息：" not in signature_text or "device-001" not in signature_text:
        _add_error(errors, "signature-canonicalization.md 的业务消息示例必须体现 UDID 行")
    websocket_message_example = re.search(
        r"WebSocket 已认证高风险业务消息（`METHOD/PATH/CANONICAL_QUERY/UDID` 均为空槽位）：\n\n```text\n(?P<body>[\s\S]*?)\n```",
        signature_text,
    )
    if not websocket_message_example:
        _add_error(errors, "signature-canonicalization.md 必须提供 WebSocket 已认证高风险业务消息 canonical 示例并说明 UDID 空槽位")
    else:
        websocket_example_body = websocket_message_example.group("body").splitlines()
        if "app_ws_001" not in websocket_message_example.group("body") or "TOKEN_UPLOAD" not in websocket_message_example.group("body"):
            _add_error(errors, "signature-canonicalization.md 的 WebSocket 高风险业务示例必须体现 api-key 和 func")
        if len(websocket_example_body) < 6 or websocket_example_body[5] != "":
            _add_error(errors, "signature-canonicalization.md 的 WebSocket 高风险业务示例必须保留空 UDID 行")
    if "可按项目映射为 Header" in signature_text:
        _add_error(errors, "signature-canonicalization.md 不应把 HTTP/WebSocket udid 来源写成固定或默认 Header 映射")
    if "HTTP/WebSocket Header | TCP/UDP Envelope" in signature_text or "HTTP/WebSocket Header | TCP/UDP Envelope 等价字段" in signature_text:
        _add_error(errors, "signature-canonicalization.md 不应继续把 WebSocket 消息级签名字段来源归入 Header/TCP-UDP 二分")
    for text in ["HTTP/REST 或 WebSocket Upgrade Header", "TCP/UDP/WebSocket 消息 Envelope 等价字段", "WebSocket `AUTH` 和高风险业务消息使用 envelope `reqid`", "WebSocket 高风险业务消息的认证主体来自已认证连接上下文", "`x-reqid/x-timestamp/x-api-key/x-sign-alg/x-api-version`", "`reqid/ts/api-key/sign-alg/version/func`", "`reqid/ts/udid/api-key/sign-alg/version/func`"]:
        if text not in signature_text:
            _add_error(errors, f"signature-canonicalization.md 的字段来源表必须覆盖 WebSocket 消息 envelope 边界：{text}")
    if "HTTP/WebSocket Header 没有等价字段" in signature_text:
        _add_error(errors, "signature-canonicalization.md 的 UDID 说明不应把 WebSocket 消息级签名字段来源写成 Header")
    if "HTTP/WebSocket Header 推荐统一为 `x-api-key`" in signature_text or "TCP/UDP envelope 推荐统一为 `api-key`" in signature_text:
        _add_error(errors, "signature-canonicalization.md 的密钥标识规则不应漏掉 WebSocket AUTH/高风险业务 envelope api-key")
    for text in [
        "SDK/OpenAPI 和 WebSocket Upgrade Header 推荐统一使用 `x-api-key`",
        "CMS HTTP/REST 不使用 `x-api-key`，使用登录主体、token 指纹和 `x-udid` 形成调用身份",
        "TCP/UDP、WebSocket `AUTH` 和已认证 WebSocket 高风险业务消息 envelope 推荐统一使用 `api-key`",
        "CMS HTTP/REST 的 `KEY_ID` 为空槽位时，签名原文仍必须保留该空行",
    ]:
        if text not in signature_text:
            _add_error(errors, f"signature-canonicalization.md 的密钥标识规则必须区分 CMS、SDK/OpenAPI、Upgrade Header 与消息 envelope：{text}")
    for text in replay_key_text:
        if text not in signature_text:
            _add_error(errors, f"signature-canonicalization.md 的 Replay key 表缺少：{text}")
    for text in ["UDP source address 只能作为风控信号", "不要只依赖 `connectionId`", "不单独承担防重放"]:
        if text not in signature_text:
            _add_error(errors, f"signature-canonicalization.md 的防重放边界缺少：{text}")
    for text in ["可短 TTL 保存脱敏传输响应摘要", "不保存业务幂等结果", "replay cache 保存的是短 TTL 传输响应摘要或重放标记", "业务幂等存储"]:
        if text not in signature_text:
            _add_error(errors, f"signature-canonicalization.md 必须区分 replay cache 与业务幂等存储：{text}")
    for text in ["高风险消息必须携带 `api-key/KEY_ID`", "不能只依赖连接级密钥上下文"]:
        if text not in signature_text:
            _add_error(errors, f"signature-canonicalization.md 的高风险消息 KEY_ID 边界缺少：{text}")
    if "高风险消息仍建议保留" in signature_text:
        _add_error(errors, "signature-canonicalization.md 不应把高风险消息 api-key/KEY_ID 描述为建议保留")
    for text in ["签名或防重放请求必填", "不得用空字符串绕过时间窗口校验"]:
        if text not in signature_text:
            _add_error(errors, f"signature-canonicalization.md 的 timestamp 必填边界缺少：{text}")
    for text in ["app_cms_001\nHMAC-SHA256", "device-001\napp_sdk_001\nHMAC-SHA256", "app_ws_001\nHMAC-SHA256"]:
        if text not in signature_text:
            _add_error(errors, f"signature-canonicalization.md 的 canonical 示例必须体现 SIGN_ALG 行：{text}")
    for text in ["CMS 公开接口和匿名公开 UDP 探测没有稳定调用身份时不进入签名 replay cache", "不能把 source address 当成稳定身份"]:
        if text not in signature_text:
            _add_error(errors, f"signature-canonicalization.md 的公开入口 replay cache 边界缺少：{text}")
    validate_signature_builder_boundaries_doc(signature_text, errors)


def validate_signature_builder_boundaries_doc(signature_text: str, errors: list[str]) -> None:
    if not signature_text:
        return
    for text in [
        "CanonicalRequest",
        "HttpRequestCanonicalBuilder",
        "WebSocketUpgradeCanonicalBuilder",
        "WebSocketAuthCanonicalBuilder",
        "WebSocketMessageCanonicalBuilder",
        "TcpAuthCanonicalBuilder",
        "TcpUdpMessageCanonicalBuilder",
    ]:
        if text not in signature_text:
            _add_error(errors, f"signature-canonicalization.md 必须按入口拆分 canonical builder：{text}")
    for text in [
        "HTTP/REST 请求体与 Query 规则",
        "必须支持 GET、POST `application/json`",
        "CMS 还必须支持 POST `application/x-www-form-urlencoded`",
        "GET | URL query 参数按名称升序和 RFC3986 编码后拼接 | 空字节数组 hash，不把 query 复制到 body",
        "POST `application/json` | 只使用 URL query，不包含 JSON 字段 | 原始 request body bytes 的 SHA-256；不要解析后重新序列化",
        "CMS POST `application/x-www-form-urlencoded` | 只使用 URL query，不包含表单字段 | 原始 form body bytes 的 SHA-256；不要解析后重新排序、重新编码或重新拼接",
        "`multipart/form-data`、文件上传和流式 body 不在默认规则内",
        "HTTP/REST GET、POST `application/json` 和 CMS POST `application/x-www-form-urlencoded` 的 query/body hash 来源",
    ]:
        if text not in signature_text:
            _add_error(errors, f"signature-canonicalization.md 必须说明 HTTP/REST query/body 签名来源：{text}")
    websocket_message_builder_line = next((line for line in signature_text.splitlines() if "`WebSocketMessageCanonicalBuilder`" in line), "")
    for text in ["已认证 WebSocket 高风险业务消息", "reqid/ts/api-key/sign-alg/version/func", "`UDID` 使用空字符串槽位", "不要要求 WebSocket 业务消息伪造 `udid`"]:
        if text not in websocket_message_builder_line:
            _add_error(errors, f"signature-canonicalization.md 的 WebSocketMessageCanonicalBuilder 职责不完整：{text}")
    if "WebSocket 高风险业务消息、TCP AUTH" not in signature_text:
        _add_error(errors, "signature-canonicalization.md 验收清单必须包含 WebSocket 高风险业务消息 canonical builder")
    for text in [
        "不要把所有入口条件写进一个巨大的 `SignatureVerifier`",
        "新增入口类型时新增 builder",
        "`SignatureVerifier` 只根据 `KEY_ID` 找密钥、校验 `sign-alg` 白名单并比较签名。",
        "`ReplayKeyResolver` 只从已解析安全字段构造 replay key。",
        "`ReplayCache` 只使用 `ReplayKeyResolver` 输出的 replay key 去重，可短 TTL 保存脱敏传输响应摘要；不重新拼 canonical string，也不构造 replay key，不保存业务幂等结果。",
    ]:
        if text not in signature_text:
            _add_error(errors, f"signature-canonicalization.md 必须说明 canonical 构造职责边界：{text}")
