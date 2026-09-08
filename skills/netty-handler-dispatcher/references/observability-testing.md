# 可观测性、测试与压测规则




## 目录

- [日志字段](#日志字段)
- [Metrics 指标](#metrics-指标)
- [告警模板](#告警模板)
- [最小测试集](#最小测试集)
- [压测指标](#压测指标)

## 日志字段

| 字段 | 说明 |
| --- | --- |
| `traceId` | 链路追踪 |
| `reqid` | 请求响应匹配 |
| `func` | 消息功能 |
| `version` | 协议版本 |
| `connectionId` | TCP/WebSocket 连接 ID；UDP 无稳定连接时为空 |
| `routeId` | UDP 上层 session 或异步响应 route ID；TCP/WebSocket 可为空 |
| `nodeId` | 节点 ID |
| `udid/userId/deviceId/clientId` | 主体标识，TCP/UDP 优先记录 `udid`，必要时脱敏 |
| `clientIp` | 客户端 IP |
| `securityStage` | 安全校验阶段，例如 `upgrade`、`auth`、`message`、`udp-message` |
| `signAlg` | 签名算法，有限枚举；签名失败时记录，不记录密钥材料 |
| `canonicalBuilder` | 签名原文构造器，有限枚举，例如 `http-rest`、`ws-upgrade`、`ws-auth`、`ws-message`、`tcp-auth`、`tcp-udp-message` |
| `contentTypeClass` | HTTP/REST body 类型归类，有限枚举，例如 `empty`、`json`、`form-urlencoded`、`multipart`、`streaming`、`unsupported`；不要记录完整 `Content-Type` 参数 |
| `bodyHashSource` | body hash 来源，有限枚举，例如 `empty-body`、`raw-json-bytes`、`raw-form-bytes`、`unsupported-body`；用于排查 GET/POST JSON/CMS 表单签名不一致 |
| `replayKeyType` | replay key 类型，例如 `ws-upgrade`、`ws-auth`、`ws-message`、`tcp`、`udp`；不要记录完整 replay key |
| `costMs` | 处理耗时 |
| `code` | 响应码 |
| `retryable` | 是否可重试 |

## Metrics 指标

统一指标优先使用 `netty_*`，通过 `transport=udp|tcp|websocket` 区分传输类型。历史项目已有 `ws_*` 指标时可以保留兼容别名，但新设计不要只覆盖 WebSocket。

| 指标 | 类型 | 标签 |
| --- | --- | --- |
| `netty_connections_active` | Gauge | `transport`, `nodeId`, `apiKeyGroup` |
| `netty_connections_open_total` | Counter | `transport`, `nodeId`, `result` |
| `netty_connections_close_total` | Counter | `transport`, `nodeId`, `closeCode`, `reason` |
| `netty_udp_routes_active` | Gauge | `nodeId`, `routeType` |
| `netty_udp_routes_created_total` | Counter | `nodeId`, `routeType`, `result` |
| `netty_udp_routes_expired_total` | Counter | `nodeId`, `routeType`, `reason` |
| `netty_messages_in_total` | Counter | `transport`, `func`, `version`, `nodeId` |
| `netty_messages_out_total` | Counter | `transport`, `func`, `version`, `nodeId` |
| `netty_message_latency_ms` | Histogram | `transport`, `nodeId`, `func`, `version`, `code` |
| `netty_message_errors_total` | Counter | `transport`, `nodeId`, `func`, `version`, `code` |
| `netty_auth_fail_total` | Counter | `transport`, `nodeId`, `reason` |
| `netty_signature_verify_total` | Counter | `transport`, `nodeId`, `stage`, `result`, `signAlg`, `canonicalBuilder` |
| `netty_signature_verify_duration_ms` | Histogram | `transport`, `nodeId`, `stage`, `result`, `signAlg`, `canonicalBuilder` |
| `netty_signature_fail_total` | Counter | `transport`, `nodeId`, `stage`, `reason`, `signAlg`, `canonicalBuilder`, `bodyHashSource`, `contentTypeClass` |
| `netty_replay_rejected_total` | Counter | `transport`, `nodeId`, `stage`, `replayKeyType`, `reason` |
| `netty_timestamp_skew_rejected_total` | Counter | `transport`, `nodeId`, `stage`, `reason` |
| `netty_heartbeat_timeout_total` | Counter | `transport`, `nodeId` |
| `netty_ack_timeout_total` | Counter | `transport`, `nodeId`, `func`, `version` |
| `netty_rate_limited_total` | Counter | `transport`, `nodeId`, `dimension`, `func` |
| `netty_dispatch_queue_size` | Gauge | `poolName`, `nodeId` |
| `netty_eventloop_blocked_total` | Counter | `transport`, `nodeId` |
| `netty_udp_datagrams_dropped_total` | Counter | `nodeId`, `reason` |
| `netty_tcp_frame_decode_errors_total` | Counter | `nodeId`, `reason` |

标签约束：

- Metrics 标签禁止使用 `reqid`、`connectionId`、`userId`、`deviceId`、手机号、IP 全量值等高基数字段。
- 高基数字段只进入结构化日志或 trace，不进入指标标签。
- `func` 和 `version` 必须是有限枚举；动态业务值不得拼入 `func`。
- `apiKeyGroup` 标签只能使用低基数的公开密钥分组、租户分组或 `public/unknown`，不得使用请求里的 `x-api-key/api-key` 原值、HMAC secret、私钥、token、完整 credential、手机号、`udid` 或高基数动态值。
- `nodeId` 用于多实例定位，核心消息延迟、错误、ACK 超时、限流和安全失败指标都应携带；`stage`、`reason`、`signAlg`、`replayKeyType`、`canonicalBuilder`、`bodyHashSource`、`contentTypeClass` 必须是有限枚举；不要把完整签名、完整 replay key、token、`api-key` 原值、完整 `Content-Type`、body 原文、body hash 原值或 `udid` 放进 metrics 标签。
- `netty_signature_verify_total` 和 `netty_signature_verify_duration_ms` 必须覆盖成功和失败验签路径；`result` 只能使用 `success/fail/skipped` 这类有限枚举，用于评估正常请求的 HMAC 成本和算法退化。
- 出站响应和 ACK 指标的 `func/version` 标签必须来自入站请求/通知上下文或 `data.ackFunc` 对应的协议上下文，不能为了打指标把 `func/version/traceId/status` 放回响应 JSON 顶层。
- `netty_connections_*` 只表达 TCP/WebSocket 连接；UDP 不应伪造连接数，使用 `netty_udp_routes_*` 和 `netty_udp_datagrams_dropped_total` 观察短 TTL route 与 datagram 丢弃。

高 QPS 日志采样：

- 成功的心跳、ACK、低风险通知可以采样记录，默认建议 `1%` 或按连接异常状态提升采样率。
- 错误、鉴权失败、限流、协议解析失败、签名失败、重放拦截必须全量记录结构化日志。
- 正常协议拒绝或业务失败不是程序异常，例如鉴权失败、签名失败、重放请求、参数错误、资源不存在、状态不允许、限流命中和幂等冲突。它们必须返回稳定错误码并记录结构化访问/安全日志和 `netty_*` 指标，但不得主动抛异常并打印 `log.error` 堆栈污染健壮性判断。
- 禁止吞异常。Netty handler、dispatcher、pipeline、鉴权、协议解析、ACK 写出、UDP route 和集群路由组件捕获并在当前层处理程序异常、依赖异常、编码错误、写出失败或其他不可预期异常时，必须使用 `log.error` 记录脱敏异常日志，至少包含 `transport/nodeId/reqid/func/version/securityStage/code/exceptionType`；不得空 catch、只写注释、只返回默认值或只使用 `log.warn`。只有继续 `throw` 给上层统一异常处理器的场景可以不在当前层重复打印。
- 采样日志不得影响 metrics 计数，metrics 必须基于真实事件全量统计。

## 告警模板

| 告警 | 建议条件 | 影响 |
| --- | --- | --- |
| 连接数异常下降 | `netty_connections_active` 5 分钟下降超过 30% | 服务重启、网关异常或客户端断连 |
| 鉴权失败突增 | `netty_auth_fail_total` 5 分钟同比突增 | 鉴权服务异常或攻击 |
| 签名失败突增 | `netty_signature_fail_total` 5 分钟同比突增 | 客户端签名实现异常、密钥配置错误或攻击 |
| 重放拦截突增 | `netty_replay_rejected_total` 5 分钟同比突增 | 重放攻击、客户端 `reqid` 生成异常或重试策略错误 |
| 时间戳偏差拒绝突增 | `netty_timestamp_skew_rejected_total` 5 分钟同比突增 | 客户端时钟漂移、时区/毫秒秒级混用或攻击 |
| 心跳超时突增 | `netty_heartbeat_timeout_total` 突增 | 网络抖动、服务阻塞或客户端异常 |
| P99 延迟过高 | 核心 `func` P99 超过业务阈值 | 用户体验下降 |
| 错误率过高 | 核心 `func` 错误率超过阈值 | 业务不可用风险 |
| ACK 超时过高 | `netty_ack_timeout_total` 超过阈值 | 推送不可达 |
| EventLoop 阻塞 | `netty_eventloop_blocked_total` 持续增长 | I/O 线程被慢操作拖住 |
| 业务线程池积压 | `netty_dispatch_queue_size` 持续增长 | 下游依赖慢或容量不足 |
| Redis/MQ/DB 超时突增 | 依赖超时率超过阈值 | 状态读写或异步投递异常 |

仪表盘至少包含：

- 当前在线连接数、连接建立/关闭速率。
- UDP route 数、route 创建/过期速率、datagram 丢弃原因。
- 按 `nodeId + func` 的 QPS、错误率、P95/P99、ACK 超时和限流率。
- 按 `nodeId` 展示鉴权失败、签名失败、重放拦截、时间戳偏差拒绝和心跳超时。
- 业务线程池队列、拒绝次数、EventLoop 阻塞。
- Redis/MQ/DB 依赖耗时和错误率。

## 最小测试集

| 测试类型 | 必测内容 |
| --- | --- |
| 协议解析测试 | 缺字段、字段类型错误、未知 `func`、未知 `version`、超大 payload |
| handler 分发测试 | `func + version` 命中正确 handler，重复 key 启动失败 |
| 鉴权测试 | 未鉴权消息被拒绝、鉴权失败关闭、权限不足拒绝 |
| 心跳测试 | 正常心跳续期、心跳超时关闭 |
| 幂等测试 | 同一 `reqid` 重放、同一业务流水重试 |
| 顺序测试 | 同连接多消息并发处理后响应能用 `reqid` 匹配 |
| 异常测试 | handler 抛异常、Redis/MQ/DB 超时、业务超时 |
| 安全测试 | 重放攻击、签名错误、时间戳超窗、消息过大、敏感日志检查；HTTP/REST 覆盖 GET query 排序、POST `application/json` 原始 body hash、CMS POST `application/x-www-form-urlencoded` 原始表单 body hash，并验证 `canonicalBuilder/bodyHashSource/contentTypeClass` 日志字段和 `netty_signature_fail_total`、`netty_replay_rejected_total`、`netty_timestamp_skew_rejected_total` 递增 |
| 兼容测试 | 旧 UDP/TCP/HTTP 入口与新 Netty UDP/TCP/WebSocket 入口业务结果一致 |

## 压测指标

- 连接数：最大在线连接、连接建立速率、断线重连速率。
- 吞吐：总 QPS、单连接 QPS、按 `func` 分组 QPS。
- 延迟：P50/P90/P95/P99。
- 资源：CPU、内存、GC、线程池队列、Netty event loop 阻塞时间。
- 依赖：Redis/MQ/DB/HTTP 超时率和耗时。
- 稳定性：长连接 1 小时以上 soak test、网络抖动、服务重启恢复。
- 安全性：签名失败率、重放拦截率、时间戳偏差拒绝率；压测时必须验证安全失败事件不会进入业务 handler。
- UDP 稳定性：datagram 丢弃率、乱序/重复率、route 过期率和固定入口节点切换恢复。

验收阈值必须由项目按业务目标给出。没有业务阈值时，不要声称性能达标，只能说明“已完成压测方法设计”。
