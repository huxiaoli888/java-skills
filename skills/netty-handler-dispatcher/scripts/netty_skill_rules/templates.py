from __future__ import annotations

import re

from netty_skill_rules.markdown import validate_templates_markdown


def _add_error(errors: list[str], message: str) -> None:
    errors.append(message)


TemplateRuleGroups = dict[str, list[str]]


def _require_texts(templates_text: str, errors: list[str], texts: list[str], message_prefix: str) -> None:
    for text in texts:
        if text not in templates_text:
            _add_error(errors, f"{message_prefix}：{text}")


def validate_templates_core_doc(templates_text: str, errors: list[str], template_rule_groups: TemplateRuleGroups) -> None:
    _require_texts(
        templates_text,
        errors,
        template_rule_groups["templateMaintenanceBoundaryText"],
        "templates.md 必须说明模板维护边界",
    )
    if "TokenStatusNotifyHandler" in templates_text:
        _add_error(errors, "templates.md 不应把服务端通知写成入站 handler")
    if "TokenStatusNotifyPublisher / NettyResponseWriter" not in templates_text:
        _add_error(errors, "templates.md 的服务端通知必须使用 publisher/writer 语义")
    if "| AUTH | V1 | C -> S | 否 | TcpAuthHandler / WsAuthMessageHandler | AuthApplicationService / AuthContextResolver | TCP 首条认证或 WebSocket auth-message 首条认证 |" not in templates_text:
        _add_error(errors, "templates.md 必须把认证 func 统一为 AUTH 并覆盖 TCP/WebSocket auth-message")
    if "handler / publisher" not in templates_text:
        _add_error(errors, "templates.md 的 func 列表必须区分 handler 和 publisher")
    if "connectionEpoch" not in templates_text:
        _add_error(errors, "templates.md 的集群路由模板必须包含 connectionEpoch")
    if "# Netty 长连接集群路由设计" in templates_text:
        _add_error(errors, "templates.md 的集群路由模板标题不应只写 Netty 长连接")
    if "# Netty 连接与通知集群路由设计" not in templates_text:
        _add_error(errors, "templates.md 的集群路由模板标题必须覆盖连接与通知路由")
    if "TCP/UDP 约束" not in templates_text or "DEVICE_PING" not in templates_text:
        _add_error(errors, "templates.md 必须包含 TCP/UDP 协议模板细节")
    _require_texts(
        templates_text,
        errors,
        template_rule_groups["templateConfigParameterText"],
        "templates.md 的协议说明书模板必须包含配置参数清单",
    )
    _require_texts(
        templates_text,
        errors,
        template_rule_groups["templateResponseAckBoundaryText"],
        "templates.md 的协议说明书模板必须包含响应和 ACK 字段边界",
    )


def validate_templates_security_constraints(templates_text: str, errors: list[str], template_http_rest_text: list[str]) -> None:
    for text in template_http_rest_text:
        if text not in templates_text:
            _add_error(errors, f"templates.md 的协议说明书模板必须覆盖 HTTP/REST CMS/SDK 签名约束：{text}")
    if "CMS 和 SDK 的 HTTP/REST 请求头使用 `authorization/x-reqid/x-timestamp/x-sign/x-sign-alg/x-api-version/x-api-key`" in templates_text:
        _add_error(errors, "templates.md 不应把 CMS HTTP/REST 和 SDK/OpenAPI 合并为同一套 x-api-key 请求头")
    if "公开接口可以没有 `authorization`，但需要签名防篡改时仍必须携带 `x-reqid/x-timestamp/x-sign/x-sign-alg/x-api-version/x-api-key`" in templates_text:
        _add_error(errors, "templates.md 不应要求 CMS 公开接口签名时携带 x-api-key")
    for text in [
        "TCP/UDP/WebSocket 高风险消息级签名",
        "## WebSocket 消息级签名约束",
        "WebSocket 鉴权模式必须显式选择：`signed-upgrade`、`auth-message` 或 `hybrid`",
        "`signed-upgrade`：Upgrade 阶段使用 HTTP Header",
        "`WebSocketUpgradeCanonicalBuilder`",
        "ws-upgrade:{x-api-key}:{x-reqid}:{authSubject|clientId}",
        "`auth-message`：Upgrade 只做 path、Origin、基础限流和短期票据校验",
        "首条 `AUTH` 使用 envelope 顶层 `reqid/ts/api-key/sign-alg/version/func` 和原始消息体 bytes",
        "`WebSocketAuthCanonicalBuilder`",
        "ws-auth:{api-key}:{reqid}:{ticketId|authSubject|connectionId}",
        "`hybrid`：优先执行 `signed-upgrade`",
        "缺少完整签名 Header 时进入 `auth-message` 短认证窗口",
        "WebSocket Upgrade 阶段使用 HTTP Header",
        "WebSocket 首条 `AUTH` 使用 envelope 顶层",
        "已认证 WebSocket 高风险业务消息必须在 envelope 顶层携带 `sign/sign-alg/api-key`",
        "WebSocket 高风险业务防重放维度：`ws-message:{api-key}:{reqid}:{authSubject|connectionId}`",
        "不要把 HTTP `x-*` Header 字段放入 `payload`",
        "无 `udid` 时 `UDID` 槽位使用空字符串",
        "WebSocket 高风险业务签名原文包含 `reqid + ts + api-key + sign-alg + func + version + payloadHash`",
    ]:
        if text not in templates_text:
            _add_error(errors, f"templates.md 的协议说明书模板必须覆盖 WebSocket 消息级签名约束：{text}")
    if "WebSocket 高风险业务签名原文包含 `reqid + ts + api-key + func + version + payloadHash`" in templates_text:
        _add_error(errors, "templates.md 的 WebSocket 高风险签名原文不应漏掉 sign-alg")
    if "UDP 消息级签名 |" in templates_text:
        _add_error(errors, "templates.md 的鉴权方式不应只写 UDP 消息级签名，必须覆盖 TCP/UDP/WebSocket 高风险消息级签名")


def validate_templates_response_footer(templates_text: str, errors: list[str], template_rule_groups: TemplateRuleGroups) -> None:
    _require_texts(
        templates_text,
        errors,
        template_rule_groups["templateResponseFooterText"],
        "templates.md 的错误码和 ACK 模板必须包含",
    )
    if re.search(r"\bAC000\d\b|\bAC9999\b", templates_text):
        _add_error(errors, "templates.md 不应复制具体 AC000x/AC9999 错误码，具体 code 归 response-contract.md")


def validate_templates_tcp_udp_examples(templates_text: str, errors: list[str], template_rule_groups: TemplateRuleGroups) -> None:
    _require_texts(
        templates_text,
        errors,
        template_rule_groups["templateTcpUdpFieldText"],
        "templates.md 的 TCP/UDP 协议模板缺少字段要求",
    )
    _require_texts(
        templates_text,
        errors,
        template_rule_groups["templateTcpUdpAnonymousText"],
        "templates.md 的 TCP/UDP 协议模板必须说明匿名公开探测边界",
    )
    device_ping_line = next((line for line in templates_text.splitlines() if line.startswith("| DEVICE_PING |")), "")
    if not device_ping_line:
        _add_error(errors, "templates.md 的 func 列表必须包含 DEVICE_PING")
    else:
        if "匿名公开探测可省略" in device_ping_line:
            _add_error(errors, "templates.md 的 DEVICE_PING 行不应把已识别设备探活和匿名公开探测混写")
        for text in template_rule_groups["templateDevicePingLineText"]:
            if text not in device_ping_line:
                _add_error(errors, f"templates.md 的 DEVICE_PING 行必须明确设备探活边界：{text}")
    public_ping_line = next((line for line in templates_text.splitlines() if line.startswith("| PUBLIC_PING |") or line.startswith("| HEALTH_CHECK |")), "")
    if not public_ping_line:
        _add_error(errors, "templates.md 的 func 列表必须单独列出 PUBLIC_PING 或 HEALTH_CHECK 作为匿名公开探测")
    else:
        for text in template_rule_groups["templatePublicPingLineText"]:
            if text not in public_ping_line:
                _add_error(errors, f"templates.md 的匿名公开探测行必须明确边界：{text}")
    if "兼容旧 UDP/HTTP" in templates_text:
        _add_error(errors, "templates.md 的兼容性模板必须覆盖旧 UDP/TCP/HTTP 或旧入口")
    if "Implementation Plan 模板" in templates_text or "TcpFrameDecoder" in templates_text:
        _add_error(errors, "templates.md 不应继续承载实现计划模板，改读 implementation-plan.md")


def validate_templates_signature_cost_metrics(templates_text: str, errors: list[str], template_rule_groups: TemplateRuleGroups) -> None:
    _require_texts(
        templates_text,
        errors,
        template_rule_groups["templateSignatureCostMetricText"],
        "templates.md 的压测报告模板必须覆盖正常验签成本指标",
    )


def validate_templates_cluster_template(templates_text: str, errors: list[str], template_rule_groups: TemplateRuleGroups) -> None:
    if "netty:conn:{connectionId}" not in templates_text:
        _add_error(errors, "templates.md 的集群路由模板必须使用通用 netty:conn Key")
    _require_texts(
        templates_text,
        errors,
        template_rule_groups["templateClusterConnectionBoundaryText"],
        "templates.md 的集群路由模板必须覆盖连接和 UDP route 边界",
    )
    _require_texts(
        templates_text,
        errors,
        template_rule_groups["templateClusterRouteFlowText"],
        "templates.md 的集群路由模板必须区分 TCP/WebSocket 连接和 UDP route 流程",
    )
    _require_texts(
        templates_text,
        errors,
        template_rule_groups["templateClusterCleanupText"],
        "templates.md 的集群路由模板必须覆盖 routeEpoch 清理边界",
    )
    _require_texts(
        templates_text,
        errors,
        template_rule_groups["templateClusterOpsRecoveryText"],
        "templates.md 的集群路由模板必须覆盖节点运维恢复语义",
    )
    if "TCP/UDP 设备或用户唯一标识在线连接集合" in templates_text:
        _add_error(errors, "templates.md 不应把 UDP udid 直接描述为持久在线 connectionId 集合")
    if "UDP route 只用于短 TTL 异步响应或上层 session" not in templates_text:
        _add_error(errors, "templates.md 的集群路由模板必须说明 UDP route 短 TTL 边界")
    if "按 transport 写 Channel 或 UDP 响应 endpoint" not in templates_text:
        _add_error(errors, "templates.md 的集群路由模板必须区分连接写回和 UDP endpoint 写回")
    _require_texts(
        templates_text,
        errors,
        template_rule_groups["templateClusterSequenceBoundaryText"],
        "templates.md 的 WebSocket 消息级签名约束必须明确低风险业务顺序字段边界",
    )
    _require_texts(
        templates_text,
        errors,
        template_rule_groups["templateClusterNotificationMetricText"],
        "templates.md 的集群路由模板必须覆盖通知和 UDP 异步响应",
    )


def validate_templates_load_report_metrics(templates_text: str, errors: list[str], template_rule_groups: TemplateRuleGroups) -> None:
    _require_texts(
        templates_text,
        errors,
        template_rule_groups["templateLoadReportMetricText"],
        "templates.md 的压测报告模板必须覆盖 UDP route/datagram 和安全事件指标",
    )


def validate_templates_doc(
    templates_text: str,
    errors: list[str],
    template_http_rest_text: list[str],
    template_rule_groups: TemplateRuleGroups,
) -> None:
    if not templates_text:
        return
    validate_templates_core_doc(templates_text, errors, template_rule_groups)
    validate_templates_security_constraints(templates_text, errors, template_http_rest_text)
    validate_templates_response_footer(templates_text, errors, template_rule_groups)
    validate_templates_tcp_udp_examples(templates_text, errors, template_rule_groups)
    validate_templates_signature_cost_metrics(templates_text, errors, template_rule_groups)
    validate_templates_cluster_template(templates_text, errors, template_rule_groups)
    validate_templates_load_report_metrics(templates_text, errors, template_rule_groups)
    validate_templates_markdown(templates_text, errors)
