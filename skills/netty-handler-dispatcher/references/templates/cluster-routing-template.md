## 集群路由设计模板

````markdown
# Netty 连接与通知集群路由设计

## 目标

- 支持多实例部署。
- 支持服务端通知路由到连接所在节点。
- 支持 ACK、重试和节点下线处理。

## 节点和连接标识

| 标识 | 生成方 | 用途 |
| --- | --- | --- |
| `nodeId` | 服务端实例 | 标识连接或 route 所在节点 |
| `connectionId` | 服务端 | 标识 TCP/WebSocket 单条连接 |
| `connectionEpoch` | 服务端 | 防止旧 TCP/WebSocket 连接 close 清理新连接映射 |
| `routeId` | 服务端 | 标识 UDP 上层 session 或异步响应 route，短 TTL，不代表稳定连接 |
| `routeEpoch` | 服务端 | 防止旧 UDP route 过期清理新 route 映射 |
| `userId/deviceId/udid` | 鉴权结果、TCP/UDP envelope 或上层 session | 在线映射和业务路由 |

## 在线映射

| Key | Value | TTL | 说明 |
| --- | --- | --- | --- |
| `netty:conn:{connectionId}` | `transport,nodeId,userId,deviceId,udid,connectionEpoch,connectedAt` | 心跳续期 | TCP/WebSocket 连接到节点和身份 |
| `netty:udp-route:{routeId}` | `nodeId,udid,remoteAddress,routeEpoch,createdAt,lastSeenAt` | 短 TTL | UDP 上层 session 或异步响应路由；不能把 source address 当成稳定身份 |
| `netty:user:{userId}` | `connectionId/routeId` set/zset | 心跳或短 TTL 续期 | 用户在线连接或 UDP 上层路由集合 |
| `netty:device:{deviceId}` | `connectionId/routeId` set/zset | 心跳或短 TTL 续期 | 设备在线连接或 UDP 上层路由集合 |
| `netty:udid:{udid}` | `connectionId/routeId` set/zset | 心跳或短 TTL 续期 | TCP/WebSocket 连接或 UDP 上层路由集合 |
| `netty:node:{nodeId}` | `connectionId/routeId` set/zset | 心跳或短 TTL 续期 | 节点下线清理 |

## 连接注册与清理

```text
TCP/WebSocket 鉴权成功，或 UDP 上层 route 创建成功
  -> TCP/WebSocket 生成 connectionId + connectionEpoch 并写本机 ChannelRegistry
  -> UDP 上层 session 或异步响应生成 routeId + routeEpoch
  -> 写 Redis 在线映射或短 TTL route，并设置 TTL
  -> 心跳或短 TTL 续期时校验 connectionEpoch/routeEpoch
  -> close 或 route 过期清理时仅删除 connectionEpoch/routeEpoch 匹配的映射
```

## 路由方案

采用：

- 本节点直发：
- 跨节点通知：
- 关键通知：
- 非关键通知：
- 离线消息：

## 通知流程

```text
业务产生通知
  -> 查询 user/device/udid 在线映射
  -> 查询 connectionId/routeId -> nodeId
  -> 本节点直发或投递到目标节点通道/stream
  -> 目标节点按 transport 写 Channel 或 UDP 响应 endpoint；UDP route 只用于短 TTL 异步响应或上层 session
  -> 等待 ACK 或记录发送结果
```

## 失败处理

| 场景 | 处理 |
| --- | --- |
| Redis 映射不存在 | 进入离线消息或丢弃 |
| 旧连接 close 或旧 route 过期晚于新映射注册 | `connectionEpoch/routeEpoch` 不匹配则忽略旧 close 或旧 route |
| nodeId 不可达 | 重试 / 死信 / 离线消息 |
| Channel 不存在或 UDP endpoint 已过期 | 清理脏映射 |
| 客户端未 ACK | 重发，超过次数标记失败 |
| 节点下线 | 清理本节点 TCP/WebSocket 连接映射和 UDP route 映射，Redis TTL 作为兜底 |
| 服务重启 | TCP/WebSocket 客户端重连，UDP route 由短 TTL 过期或由上层 session 重建，业务状态从 Redis/DB/MQ 恢复 |
| 节点滚动发布 | 先停止接新 TCP/WebSocket 连接和新 UDP route，再等待旧连接迁移、route 过期或超时关闭 |
| 中间件积压 | 降级为客户端主动查询 |

## 验收

- 跨节点通知或异步响应成功率：
- ACK 超时率：
- Redis 脏映射清理：
- 节点重启恢复：
- 节点下线映射清理：
- 滚动发布期间连接迁移和 UDP route 过期：
- 在线状态结合心跳时间、route `lastSeenAt` 和节点健康，不只依赖 Redis key：
````
