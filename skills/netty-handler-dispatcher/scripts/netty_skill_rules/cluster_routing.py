from __future__ import annotations

import re


def _add_error(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_cluster_routing_doc(cluster_text: str, errors: list[str]) -> None:
    if not cluster_text:
        return

    stale_websocket_only_intro = "WebSocket 上生产" + "必须按多实例设计"
    stale_websocket_node_consumer = "WebSocket 节点" + "作为 consumer"
    if stale_websocket_only_intro in cluster_text:
        _add_error(errors, "cluster-routing.md 不应只按 WebSocket 描述集群路由")
    if stale_websocket_node_consumer in cluster_text:
        _add_error(errors, "cluster-routing.md 的跨节点消费说明应使用 Netty 节点等通用表述")
    if "netty:conn:{connectionId}" not in cluster_text or "transport,nodeId" not in cluster_text:
        _add_error(errors, "cluster-routing.md 的在线映射 Key 必须使用通用 netty: 前缀并记录 transport")
    for text in [
        "TCP/WebSocket 每条连接唯一",
        "TCP/WebSocket 每次连接注册递增或随机生成，用于防止旧连接清理新连接",
        "UDP 上层 session 或异步响应 route 唯一标识，短 TTL，不代表稳定连接",
        "每次 UDP route 注册递增或随机生成，用于防止旧 route 过期清理新 route",
        "userId/deviceId/udid -> connectionId[]/routeId[]",
        "netty:udp-route:{routeId}",
        "netty:udid:{udid}",
        "connectionId/routeId",
        "transport,nodeId,userId,deviceId,udid,connectionEpoch,connectedAt",
        "UDP endpoint 已过期",
    ]:
        if text not in cluster_text:
            _add_error(errors, f"cluster-routing.md 的在线映射必须覆盖连接和 UDP route 边界：{text}")
    for text in ["TCP/WebSocket 连接鉴权成功，或 UDP 上层 route 创建成功", "按 transport 写本机 Channel 或 UDP 响应 endpoint"]:
        if text not in cluster_text:
            _add_error(errors, f"cluster-routing.md 的流程必须区分 TCP/WebSocket 连接和 UDP route：{text}")
    if "TCP/UDP 设备或用户唯一标识在线连接集合" in cluster_text or "查询 user/device/udid 对应 connectionId\n" in cluster_text:
        _add_error(errors, "cluster-routing.md 不应把 UDP udid 直接描述为持久在线 connectionId 集合")
    if "查询 user/device 对应 connectionId" in cluster_text:
        _add_error(errors, "cluster-routing.md 的服务端通知路由必须包含 udid")
    if "查询 user/device/udid 对应 connectionId 或 routeId" not in cluster_text:
        _add_error(errors, "cluster-routing.md 的服务端通知路由必须按 user/device/udid 查询 connectionId 或 routeId")
    for text in ["UDP route 只能用于短 TTL 异步响应或上层 session", "按 transport 写 Channel 或 UDP 响应 endpoint", "不能把 source address 当成稳定身份"]:
        if text not in cluster_text:
            _add_error(errors, f"cluster-routing.md 必须说明 UDP route 边界：{text}")
    for text in [
        "UDP 只在上层 session 或异步响应场景使用 route",
        "连接映射和 UDP route 映射",
        "UDP route 由短 TTL 过期或由上层 session 重建",
        "TCP/WebSocket 心跳续期校验 connectionEpoch，UDP route 短 TTL 续期校验 routeEpoch",
        "关闭连接或 UDP route 过期时只能删除 `connectionEpoch/routeEpoch`",
        "route `lastSeenAt`",
        "本节点连接或 route：本地直发或 UDP endpoint 响应",
        "UdpRouteRegistry",
        "`transport`、`connectionId/routeId`",
        "connectionId` 或 `routeId`",
        "不应把原 datagram 地址当作长期在线路由",
        "本地连接/route 和跨节点连接/route",
    ]:
        if text not in cluster_text:
            _add_error(errors, f"cluster-routing.md 后半部分必须贯穿 UDP route 边界：{text}")
    for text in ["只发给本节点连接：使用本地内存直发", "每个节点维护本机 `ChannelRegistry`。", "payload 必须包含 `connectionId`、", "本节点消费后写 Channel", "节点下线时必须清理本节点连接映射，Redis TTL 作为兜底", "服务重启后客户端重连，业务状态从 Redis/DB/MQ 恢复"]:
        if text in cluster_text:
            _add_error(errors, f"cluster-routing.md 后半部分仍存在纯连接模型旧表述：{text}")
