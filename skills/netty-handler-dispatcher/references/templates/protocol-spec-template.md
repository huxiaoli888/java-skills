
## Netty 传输协议说明书模板

````markdown
# Netty 传输协议说明书

## 基本信息

| 项 | 值 |
| --- | --- |
| Transport | UDP / TCP / WebSocket |
| Endpoint / Port | `/ws/{business-domain}` 或 TCP/UDP 端口 |
| 实现 | Netty UDP / Netty TCP / Netty WebSocket |
| 编码 | JSON / Protobuf / Binary |
| 默认版本 | `V1` |
| 鉴权方式 | HTTP/REST CMS/SDK 签名 / `signed-upgrade` / `auth-message` / AUTH / TCP/UDP/WebSocket 高风险消息级签名 |
| 心跳 func | `HEARTBEAT` |

## 配置参数清单

| 参数 | 值 | 说明 |
| --- | --- | --- |
| `websocket.auth-timeout-ms` | | WebSocket `auth-message` 首条 `AUTH` 认证窗口 |
| `websocket.max-frame-payload-length` | | WebSocket 单帧最大 payload |
| `tcp.max-frame-bytes` | | TCP 单帧最大长度 |
| `tcp.auth-timeout-ms` | | TCP 建连后首条 `AUTH` 认证窗口 |
| `tcp.reader-idle-seconds` | | TCP 心跳或读空闲超时 |
| `udp.max-datagram-bytes` | | UDP 单个 datagram 最大业务负载 |
| `udp.route-ttl-seconds` | | UDP 上层 route 或异步响应 endpoint 短 TTL |
| `security.timestamp-skew-seconds` | | `ts/x-timestamp` 与服务端时间允许偏差 |
| `security.replay-ttl-seconds` | | `reqid/x-reqid` replay key 短 TTL 去重窗口 |
| `rate-limit.max-qps-per-udid` | | 设备或用户维度限流 |

## 连接生命周期

```text
CONNECT -> AUTHENTICATING -> AUTHENTICATED -> ACTIVE -> IDLE -> CLOSING -> CLOSED
```

## Envelope

请求、响应、错误、通知、ACK 结构见 `references/protocol-format.md`。

## 响应和 ACK 字段边界

- 响应和 ACK 统一使用 `reqid/code/message/ts/data`。
- 响应和 ACK 顶层禁止返回 `func/version/traceId/status`。
- 成功响应和成功 ACK 固定 `code=000000`；失败码必须使用 `SMEEEE` 格式的稳定字符串错误码。
- 禁止的是响应或 ACK 顶层协议状态字段；业务 `payload` 或 `data` 内部可以包含订单状态、设备状态、令牌状态等领域字段，但不得替代统一 `code`。
- ACK 确认对象放在 `data.ackFunc`，确认状态放在 `data.ackStatus`。
- ACK 的 `message` 使用中文提示，机器枚举值不要写进 `message`。
- ACK 属于响应类消息，不作为入站业务 `func + version` 注册 handler；入站 ACK 由协议层或统一 writer/dispatcher 的 pending-ack 边界处理。

## HTTP/REST CMS/SDK 签名约束

- CMS HTTP/REST 登录后受保护接口使用 `authorization/x-udid/x-reqid/x-timestamp/x-sign/x-sign-alg/x-api-version`，不使用 `x-api-key` 作为后台公参。
- SDK/OpenAPI HTTP/REST 接口使用 `authorization/x-reqid/x-timestamp/x-sign/x-sign-alg/x-api-version/x-api-key`，其中 `authorization` 只在需要登录态时携带。
- 登录、验证码、公开探活等 CMS 公开接口默认不需要 `authorization`、签名或 `x-udid`，不进入签名 replay cache；如项目要求公开接口也签名，只携带 `x-reqid/x-timestamp/x-sign/x-sign-alg/x-api-version`，并按 `path + clientIp + x-reqid` 叠加限流。
- CMS 和 SDK/OpenAPI 都必须支持 GET 与 POST `application/json` 的签名防篡改。
- CMS 还必须支持 POST `application/x-www-form-urlencoded` 表单提交的签名防篡改。
- GET 的 `CANONICAL_QUERY` 来自 URL query，`BODY_SHA256_HEX` 使用空字节数组 hash，不把 query 复制到 body。
- POST `application/json` 的 `BODY_SHA256_HEX` 使用原始 request body bytes，不解析后重新序列化。
- CMS POST `application/x-www-form-urlencoded` 的 `BODY_SHA256_HEX` 使用原始 form body bytes，不解析后重新排序或重新编码；表单字段属于 body，不属于 query。
- `multipart/form-data`、文件上传和流式 body 不在默认规则内，需要单独定义摘要字段或上传前置签名策略。

## TCP/UDP 约束

- TCP 拆包/粘包方案：
- TCP 最大帧长度：
- UDP 最大 datagram：
- UDP 丢包、乱序、重复处理：
- UDP 是否允许重试：
- UDP 幂等键：
- TCP/UDP 顶层身份字段：高风险或已识别设备请求使用 `udid`；匿名公开探测可省略 `udid`
- TCP/UDP 顶层签名字段：高风险、需鉴权或需防篡改请求使用 `authorization/sign/sign-alg/api-key`；匿名公开探测可省略并改由限流和风控兜底
- TCP/UDP 防重放维度：高风险或已识别设备请求使用 `reqid + ts + api-key + udid`；匿名公开探测按 IP、端口和 `func` 限流
- TCP/UDP 顺序字段：仅有顺序语义的业务使用 `seqno`，无顺序语义的探测或查询不要强制携带

## WebSocket 消息级签名约束

- WebSocket 鉴权模式必须显式选择：`signed-upgrade`、`auth-message` 或 `hybrid`。
- `signed-upgrade`：Upgrade 阶段使用 HTTP Header `authorization/x-reqid/x-timestamp/x-sign/x-sign-alg/x-api-version/x-api-key`，使用 `WebSocketUpgradeCanonicalBuilder` 构造签名原文，并按 `ws-upgrade:{x-api-key}:{x-reqid}:{authSubject|clientId}` 防重放。
- `auth-message`：Upgrade 只做 path、Origin、基础限流和短期票据校验；首条 `AUTH` 使用 envelope 顶层 `reqid/ts/api-key/sign-alg/version/func` 和原始消息体 bytes，通过 `WebSocketAuthCanonicalBuilder` 构造签名原文，并按 `ws-auth:{api-key}:{reqid}:{ticketId|authSubject|connectionId}` 防重放。
- `hybrid`：优先执行 `signed-upgrade`；缺少完整签名 Header 时进入 `auth-message` 短认证窗口，窗口内未完成 `AUTH` 必须关闭连接。
- WebSocket Upgrade 阶段使用 HTTP Header：`authorization/x-reqid/x-timestamp/x-sign/x-sign-alg/x-api-version/x-api-key`。
- WebSocket 首条 `AUTH` 使用 envelope 顶层 `reqid/func/version/ts/sign/sign-alg/api-key`，短期票据或 token 放在 `payload` 或认证字段中。
- 已认证 WebSocket 低风险业务消息可依赖连接认证和 `reqid`；只有具备业务顺序语义的低风险消息才使用 `payload.seqno`，且 `seqno` 不替代 `reqid`。
- 已认证 WebSocket 高风险业务消息必须在 envelope 顶层携带 `sign/sign-alg/api-key`，不要把 HTTP `x-*` Header 字段放入 `payload`。
- WebSocket 高风险业务防重放维度：`ws-message:{api-key}:{reqid}:{authSubject|connectionId}`；优先使用已认证主体，`connectionId` 仅兜底。
- WebSocket 高风险业务签名原文包含 `reqid + ts + api-key + sign-alg + func + version + payloadHash`，无 `udid` 时 `UDID` 槽位使用空字符串。

## Func 列表

| func | version | 方向 | 是否需要 ACK | handler / publisher | service | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| HEARTBEAT | V1 | C -> S | 否 | HeartbeatHandler | - | 心跳 |
| DEVICE_PING | V1 | C -> S | 否 | DevicePingHandler | DeviceHeartbeatService | TCP/UDP 已识别设备探活需携带 `udid`；WebSocket 已认证连接可依赖连接身份；无顺序语义时不需要 `seqno` |
| PUBLIC_PING | V1 | C -> S | 否 | PublicPingHandler | PublicProbeService | 匿名公开探测，可省略 `udid/authorization/sign/sign-alg/api-key`，但必须限流 |
| DEVICE_STATUS_REPORT | V1 | C -> S | 否 | DeviceStatusReportHandler | DeviceStatusService | UDP/TCP 设备状态上报，有顺序语义时使用 `seqno` |
| AUTH | V1 | C -> S | 否 | TcpAuthHandler / WsAuthMessageHandler | AuthApplicationService / AuthContextResolver | TCP 首条认证或 WebSocket auth-message 首条认证 |
| TOKEN_UPLOAD | V2 | C -> S | 否 | V2TokenUploadHandler | V2TokenUpService | 上传令牌 |
| TOKEN_DOWN | V2 | C -> S | 否 | V2TokenDownHandler | V2TokenDownService | 下载令牌 |
| TOKEN_STATUS_NOTIFY | V1 | S -> C | 是 | TokenStatusNotifyPublisher / NettyResponseWriter | - | 令牌状态通知 |

## 错误码

- 错误码格式：成功固定 `000000`；失败使用 6 位字符串 `SMEEEE`，其中 `S` 为系统标识、`M` 为模块标识、`EEEE` 为 4 位错误编号。
- 具体错误码表以 `references/response-contract.md` 为准；本模板只提醒交付物需要列出本协议实际使用的 code，不在这里新增或改写错误码含义。
- 协议拒绝和正常业务失败通过稳定错误码表达，不作为异常控制流；程序异常、依赖异常和写出失败才进入 `log.error` 脱敏异常日志。

| code | retryable | 说明 | 客户端处理 |
| --- | --- | --- | --- |
| 000000 | false | 成功 | 正常处理 |
| [从 response-contract.md 引用] | [true/false] | [错误说明] | [客户端处理建议] |

## 心跳

- 客户端发送间隔：
- 服务端超时阈值：
- 超时关闭码：

## ACK 和重试

- 需要 ACK 的 func：
- ACK 超时时间：
- 最大重试次数：
- 超过次数后的处理：
- ACK 包体必须复用统一响应结构 `reqid/code/message/ts/data`；确认对象写入 `data.ackFunc`，确认状态写入 `data.ackStatus`。
- 不要新增 `ACK + V1`、`AckHandler` 或把 ACK 放入入站业务 handler registry。

## 幂等

- 请求幂等键：
- 幂等 TTL：
- 重复请求响应规则：

## 限制

- 单消息最大大小：
- 单连接 QPS：
- 单 IP 最大连接数：
- 单设备最大连接数：

## 兼容性

- 兼容旧 UDP/TCP/HTTP 或旧入口：
- 版本升级规则：
- 废弃计划：
````
