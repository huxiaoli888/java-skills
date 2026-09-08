# 集群部署与连接路由规则




## 目录

- [核心对象](#核心对象)
- [连接注册流程](#连接注册流程)
- [在线映射 Key 建议](#在线映射-key-建议)
- [服务端通知路由](#服务端通知路由)
- [集群规则](#集群规则)
- [异常处理](#异常处理)
- [路由方案取舍](#路由方案取舍)
- [方案细则](#方案细则)
- [推荐组合](#推荐组合)
- [验收清单](#验收清单)

## 核心对象

| 对象 | 存储建议 | 说明 |
| --- | --- | --- |
| `connectionId` | 本机内存 + Redis 映射 | TCP/WebSocket 每条连接唯一 |
| `connectionEpoch` | 服务端生成 | TCP/WebSocket 每次连接注册递增或随机生成，用于防止旧连接清理新连接 |
| `routeId` | 服务端 | UDP 上层 session 或异步响应 route 唯一标识，短 TTL，不代表稳定连接 |
| `routeEpoch` | 服务端生成 | 每次 UDP route 注册递增或随机生成，用于防止旧 route 过期清理新 route |
| `nodeId` | 配置或启动生成 | 当前服务实例标识 |
| `userId/deviceId/udid -> connectionId[]/routeId[]` | Redis Set/ZSet | 查询用户、设备、TCP/WebSocket 连接或 UDP 上层路由，支持多设备和多连接 |
| `connectionId/routeId -> nodeId` | Redis | 服务端通知或异步响应路由 |
| `lastHeartbeatAt` | 本机内存 + 可选 Redis | 心跳和在线状态判断 |
| 待投递通知 | MQ / Redis Stream / DB outbox | 跨节点可靠投递 |

## 连接注册流程

```text
TCP/WebSocket 连接鉴权成功，或 UDP 上层 route 创建成功
  -> TCP/WebSocket 生成 connectionId 和 connectionEpoch
  -> TCP/WebSocket 本机 ChannelRegistry 绑定 connectionId -> Channel + connectionEpoch
  -> TCP/WebSocket 写 netty:conn:{connectionId} -> transport + nodeId + userId/deviceId/udid + connectionEpoch
  -> UDP 上层 session 或异步响应写 netty:udp-route:{routeId} -> nodeId + udid + remoteAddress + routeEpoch
  -> Redis Set/ZSet 写 netty:user:{userId} / netty:device:{deviceId} / netty:udid:{udid} -> connectionId 或 routeId
  -> 设置 TTL；TCP/WebSocket 心跳续期校验 connectionEpoch，UDP route 短 TTL 续期校验 routeEpoch
```

## 在线映射 Key 建议

| Key | Value | TTL | 说明 |
| --- | --- | --- | --- |
| `netty:conn:{connectionId}` | `transport,nodeId,userId,deviceId,udid,connectionEpoch,connectedAt` | 心跳续期 | 连接到节点和身份信息 |
| `netty:udp-route:{routeId}` | `nodeId,udid,remoteAddress,routeEpoch,createdAt,lastSeenAt` | 短 TTL | UDP 上层 session 或异步响应路由；不能把 source address 当成稳定身份 |
| `netty:user:{userId}` | `connectionId/routeId` set/zset | 心跳或短 TTL 续期 | 用户在线连接或 UDP 上层路由集合 |
| `netty:device:{deviceId}` | `connectionId/routeId` set/zset | 心跳或短 TTL 续期 | 设备在线连接或 UDP 上层路由集合 |
| `netty:udid:{udid}` | `connectionId/routeId` set/zset | 心跳或短 TTL 续期 | TCP/WebSocket 连接或 UDP 上层路由集合 |
| `netty:node:{nodeId}` | `connectionId/routeId` set/zset | 心跳或短 TTL 续期 | 节点下线清理 |

清理规则：

- 关闭连接或 UDP route 过期时只能删除 `connectionEpoch/routeEpoch` 与本机记录一致的映射。
- 旧连接 close 事件不得删除新连接写入的 `user/device/udid -> connectionId/routeId` 映射。
- Redis 清理建议使用 Lua 或 compare-and-delete 语义，避免 `get -> compare -> delete` 竞态。
- TCP/WebSocket 心跳续期必须校验 `connectionEpoch`；UDP route 续期必须校验 `routeEpoch`。校验失败说明映射已经被新连接或新 route 替换，应关闭旧 Channel 或清理旧 route。
- 允许多连接时，`user/device/udid` 使用 set/zset；只允许单连接时，踢旧连接也必须带 fencing token，避免新旧连接互删。

## 服务端通知路由

```text
业务服务产生通知或异步响应
  -> 查询 user/device/udid 对应 connectionId 或 routeId
  -> 查询 connectionId/routeId 所在 nodeId
  -> 如果是本节点：按 transport 写本机 Channel 或 UDP 响应 endpoint
  -> 如果是其他节点：投递到该 nodeId 的 MQ topic / Redis Stream / pubsub
  -> 目标节点消费后按 transport 写 Channel 或 UDP 响应 endpoint；UDP route 只能用于短 TTL 异步响应或上层 session
  -> 需要 ACK 的通知记录投递状态和重试次数
```

## 集群规则

- 负载均衡层必须按传输类型确认能力：WebSocket 需要支持 HTTP Upgrade，TCP 需要支持四层转发和长连接保持，UDP 需要支持 UDP 转发或固定入口节点。
- 可以使用粘性会话降低跨节点路由成本，但不能依赖粘性会话保证正确性。
- 节点下线时必须清理本节点连接映射和 UDP route 映射，Redis TTL 作为兜底。
- 服务重启后 TCP/WebSocket 客户端重连，UDP route 由短 TTL 过期或由上层 session 重建，业务状态从 Redis/DB/MQ 恢复。
- 服务端主动通知必须可跨节点路由，不允许只查本机连接；UDP 只在上层 session 或异步响应场景使用 route。
- 多端登录策略必须明确：允许多连接、按设备多连接、踢旧连接或拒绝新连接。
- 在线状态不要只看 Redis key，需结合心跳时间、route `lastSeenAt` 和节点健康。

## 异常处理

| 场景 | 处理 |
| --- | --- |
| Redis 映射存在但本机无 Channel 或 UDP endpoint 已过期 | 删除脏映射或等待 TTL |
| 旧连接 close 或旧 route 过期晚于新映射注册 | 仅当 `connectionEpoch/routeEpoch` 匹配时删除映射，否则忽略 |
| nodeId 不存在或不可达 | 通知进入重试/死信/离线消息 |
| 客户端未 ACK | 按最大次数重发，超过后标记失败 |
| 节点滚动发布 | 先停止接新连接和新 route，再等待旧连接迁移、route 过期或超时关闭 |
| MQ 延迟过高 | 降级为客户端主动查询或丢弃非关键通知 |

## 路由方案取舍

| 方案 | 适合场景 | 延迟 | ACK/重试 | 离线消息 | 顺序性 | 复杂度 | 推荐级别 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 本地内存直发 | 连接和业务处理在同一节点 | 最低 | 仅本机内存实现 | 不支持 | 单连接可控 | 低 | 单机/本节点必备 |
| Redis Pub/Sub | 轻量跨节点通知、允许丢消息 | 低 | 不可靠，需自建 | 不支持 | 不保证 | 低 | 非关键通知可用 |
| Redis Stream | 中小规模可靠通知、需要消费确认 | 中低 | 支持 consumer group ACK | 可短期保留 | 单 stream 内相对有序 | 中 | 推荐用于可靠轻量通知 |
| RocketMQ | 业务已有 RocketMQ、需要可靠投递和重试 | 中 | 支持重试和死信 | 支持 | 分区/队列内有序 | 中高 | 推荐用于关键业务通知 |
| Kafka | 高吞吐事件流、日志型消息、跨系统订阅 | 中 | offset 语义，业务 ACK 需自建 | 支持长期保留 | 分区内有序 | 高 | 大规模事件流可用 |
| 服务内 RPC | 节点间低延迟直连、强实时 | 低 | 需要自建 | 不支持 | 请求级可控 | 中高 | 谨慎使用 |

选择规则：

- 只发给本节点连接或 route：使用本地直发或 UDP endpoint 响应。
- 非关键、可丢失、只做在线提示：Redis Pub/Sub。
- 需要可靠投递、ACK、短期重试，但规模不大：Redis Stream。
- 已有 RocketMQ 且通知影响业务结果：RocketMQ。
- 通知也是全局事件流，需要多系统订阅和长期留存：Kafka。
- 极低延迟、节点数少、可接受复杂治理：服务内 RPC。

默认组合：

```text
本节点连接或 route：本地直发或 UDP endpoint 响应
跨节点非关键通知：Redis Pub/Sub 或 Redis Stream
跨节点关键通知：RocketMQ
离线消息/长期留存：DB outbox + MQ/Stream
```

## 方案细则

### 本地直发或响应

- 每个节点维护本机 `ChannelRegistry`；如支持 UDP 上层 route，也要维护短 TTL 的 `UdpRouteRegistry` 或等价索引。
- TCP/WebSocket 写之前检查 `channel.isActive()` 和 `channel.isWritable()`。
- UDP 写回前校验 `routeEpoch`、`lastSeenAt`、`remoteAddress` 和业务 session，避免向过期 endpoint 写回。
- 发送失败时清理本地 registry/route，并触发 Redis 映射清理。
- 清理 Redis 映射时必须传入 `connectionEpoch` 或 `routeEpoch` 做条件删除。

### Redis Pub/Sub

适合非关键通知，不适合计费、令牌状态、重要业务结果通知。

- topic 可按 `nodeId` 拆分：`netty:notify:{nodeId}`。
- payload 必须包含 `transport`、`connectionId/routeId`、`reqid`、`func`、`version`。
- Pub/Sub 丢消息不可恢复，关键消息必须换可靠方案。

### Redis Stream

- stream 可按节点拆：`netty:stream:{nodeId}`。
- 每个节点作为 consumer group 消费自己的 stream。
- 消费成功后 `XACK`。
- Pending 过久的消息需要重试或转移。
- 设置保留长度或 TTL，避免 stream 无限增长。

### RocketMQ

- topic 可按业务域拆，例如 `ws-token-notify`。
- message key 使用 `reqid`、`seqno`、`connectionId` 或 `routeId`。
- tag 可使用 `func`。
- 关键消息必须设计幂等消费。
- 不建议每个连接一个 topic。

### Kafka

- partition key 可用 `userId`、`deviceId` 或业务流水。
- Netty 节点作为 consumer 消费后按 transport 写本地 Channel 或 UDP 响应 endpoint；UDP 场景没有稳定 Channel，不应把原 datagram 地址当作长期在线路由。
- ACK 语义更多是消费 offset，客户端 ACK 需要业务层另建状态。

### 服务内 RPC

- RPC 请求必须带 `reqid` 和幂等键。
- 必须设置短超时。
- 失败后不要无限重试，转入 MQ/Stream 或客户端查询兜底。

## 推荐组合

小规模初期：

```text
Redis 保存在线映射
本节点本地直发或 UDP endpoint 响应
Redis Stream 做跨节点可靠通知
```

已有 RocketMQ 的 Java 微服务：

```text
Redis 保存在线映射
本节点本地直发或 UDP endpoint 响应
RocketMQ 做关键跨节点通知
Redis Pub/Sub 做非关键在线提示
```

大规模事件平台：

```text
Redis 保存在线映射
Kafka 做全局事件流
本节点消费后按 transport 写 Channel 或 UDP 响应 endpoint
DB outbox 保存关键离线消息
```

## 验收清单

- 已说明本地连接/route 和跨节点连接/route 分别如何投递。
- 已说明通知是否允许丢失。
- 已说明是否需要客户端 ACK。
- 已说明失败重试、死信或离线消息策略。
- 已说明节点下线、滚动发布、Redis 脏映射如何处理。
- 已说明顺序性要求和分区/队列 key。
- 已说明中间件积压时的降级策略。
