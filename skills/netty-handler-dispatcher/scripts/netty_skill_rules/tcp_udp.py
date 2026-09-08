from __future__ import annotations

import re


def _add_error(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_tcp_udp_doc(tcp_udp_text: str, errors: list[str]) -> None:
    if not tcp_udp_text:
        return
    if re.search(r"\bAC000\d\b", tcp_udp_text):
        _add_error(errors, "netty-tcp-udp.md 不应直接定义 AC000x，transport 只产生类型化失败，code 由 NettyResponseWriter 按 response-contract.md 映射")
    for text in ["本文件不定义具体 `AC000x` 错误码", "TCP/UDP transport 只产生类型化失败原因", "writer/NettyResponseWriter.java", "response-contract.md"]:
        if text not in tcp_udp_text:
            _add_error(errors, f"netty-tcp-udp.md 必须说明 transport 错误码归属边界：{text}")
    if '"reqid": "same-as-request"' in tcp_udp_text or '"code": "000000"' in tcp_udp_text:
        _add_error(errors, "netty-tcp-udp.md 不应维护完整响应 JSON 示例，响应字段语义归 response-contract.md")
    if "UDP 响应使用统一响应结构，完整 JSON 示例和字段语义以 `response-contract.md` 为准" not in tcp_udp_text:
        _add_error(errors, "netty-tcp-udp.md 必须把 UDP 响应示例归口到 response-contract.md")
    for text in ["\"sign\"", "\"sign-alg\"", "\"api-key\"", "复用 envelope 已有的 `reqid`、`ts`、`version`"]:
        if text not in tcp_udp_text:
            _add_error(errors, f"netty-tcp-udp.md 的 TCP/UDP envelope 安全字段缺少：{text}")
    for text in [
        "### TCP/UDP 基础配置清单",
        "`tcp.max-frame-bytes`",
        "`tcp.auth-timeout-ms`",
        "`tcp.reader-idle-seconds`",
        "`udp.max-datagram-bytes`",
        "`udp.route-ttl-seconds`",
        "`security.timestamp-skew-seconds`",
        "`security.replay-ttl-seconds`",
        "`rate-limit.max-qps-per-udid`",
    ]:
        if text not in tcp_udp_text:
            _add_error(errors, f"netty-tcp-udp.md 必须列出 TCP/UDP 可配置参数：{text}")
    for text in ["\"udid\"", "\"seqno\"", "`udid` 表示设备或用户唯一标识"]:
        if text not in tcp_udp_text:
            _add_error(errors, f"netty-tcp-udp.md 的 TCP/UDP 请求字段缺少：{text}")
    if "TCP 也应使用 `reqid + func + version + ts + udid + payload`" in tcp_udp_text:
        _add_error(errors, "netty-tcp-udp.md 不应把 TCP 基础 envelope 写成所有请求都必须携带 udid")
    for text in [
        "TCP 基础 envelope 使用 `reqid + func + version + ts + payload`",
        "高风险请求、已识别设备请求或需要设备维度防重放的请求再携带 `udid`",
    ]:
        if text not in tcp_udp_text:
            _add_error(errors, f"netty-tcp-udp.md 必须区分 TCP 基础 envelope 与 udid 必填边界：{text}")
    tcp_auth_block = re.search(r"TCP 首条 `AUTH` 示例：[\s\S]*?```json\n(?P<body>[\s\S]*?)\n```", tcp_udp_text)
    if not tcp_auth_block:
        _add_error(errors, "netty-tcp-udp.md 必须提供 TCP 首条 AUTH 示例")
    else:
        auth_body = tcp_auth_block.group("body")
        for text in ['"func": "AUTH"', '"udid": "device-or-user-id"', '"authorization": "Bearer token"', '"sign": "signature"', '"sign-alg": "HMAC-SHA256"', '"api-key": "key-id"']:
            if text not in auth_body:
                _add_error(errors, f"netty-tcp-udp.md 的 TCP AUTH 示例缺少字段：{text}")
        for text in ['"x-reqid"', '"x-timestamp"', '"x-api-version"']:
            if text in auth_body:
                _add_error(errors, f"netty-tcp-udp.md 的 TCP AUTH 示例不应包含 HTTP x-* 字段：{text}")
    for text in ["`FUNC=AUTH`", "`BODY_SHA256_HEX`", "认证成功后才允许 `TOKEN_UPLOAD`"]:
        if text not in tcp_udp_text:
            _add_error(errors, f"netty-tcp-udp.md 的 TCP AUTH 签名或放行规则缺少：{text}")
    for text in ["应携带 `authorization` 或设备凭据、`x-reqid`", "`AUTH` payload 应包含等价于 HTTP 头的字段"]:
        if text in tcp_udp_text:
            _add_error(errors, f"netty-tcp-udp.md 不应继续要求 TCP/UDP envelope 携带 HTTP x-* 字段：{text}")
    if "sequenceNo" in tcp_udp_text:
        _add_error(errors, "netty-tcp-udp.md 不应继续使用 sequenceNo，统一使用 seqno")
    public_ping = re.search(r"公开低风险 UDP 探测请求[\s\S]*?```json\n(?P<body>[\s\S]*?)\n```", tcp_udp_text)
    if not public_ping:
        _add_error(errors, "netty-tcp-udp.md 必须提供公开低风险 UDP 探测请求示例")
    else:
        if '"func": "PUBLIC_PING"' not in public_ping.group("body"):
            _add_error(errors, "匿名公开低风险 UDP 探测请求示例必须使用 PUBLIC_PING，不应复用 DEVICE_PING")
        if '"func": "DEVICE_PING"' in public_ping.group("body"):
            _add_error(errors, "匿名公开低风险 UDP 探测请求示例不应使用 DEVICE_PING，避免混淆已识别设备探活")
        for text in ['"udid"', '"authorization"', '"sign"', '"sign-alg"', '"api-key"']:
            if text in public_ping.group("body"):
                _add_error(errors, f"匿名公开低风险 UDP 探测请求示例不应携带设备身份、鉴权或签名字段：{text}")
    device_ping_section = re.search(r'"func": "DEVICE_PING"[\s\S]*?\n\}', tcp_udp_text)
    if device_ping_section and '"udid"' not in device_ping_section.group(0):
        _add_error(errors, "DEVICE_PING 示例必须携带 udid，避免和匿名公开探测混淆")
    if device_ping_section and '"seqno"' in device_ping_section.group(0):
        _add_error(errors, "DEVICE_PING 示例不应携带 seqno，避免误导无顺序 UDP 请求")
    if "DEVICE_STATUS_REPORT" not in tcp_udp_text:
        _add_error(errors, "netty-tcp-udp.md 必须提供带 seqno 的有序 UDP 示例")
    if "按连接身份或" in tcp_udp_text:
        _add_error(errors, "netty-tcp-udp.md 不应使用按连接身份或这类模糊 replay key 表述")
    if "tcp:{api-key}:{reqid}:{udid}" not in tcp_udp_text:
        _add_error(errors, "netty-tcp-udp.md 必须明确 TCP replay key 为 tcp:{api-key}:{reqid}:{udid}")
    for text in ["reqid + ts + udid + api-key + sign-alg + func + version + payloadHash", "算法标识必须绑定进签名原文", "reqid + ts + api-key + udid"]:
        if text not in tcp_udp_text:
            _add_error(errors, f"netty-tcp-udp.md 的签名或防重放维度缺少：{text}")
    for text in ["传输响应摘要", "业务幂等结果必须由 service 层按", "不得塞进 `ReplayCache`"]:
        if text not in tcp_udp_text:
            _add_error(errors, f"netty-tcp-udp.md 必须区分 UDP retry replay 摘要与业务幂等结果：{text}")
