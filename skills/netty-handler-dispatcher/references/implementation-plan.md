# Implementation Plan 模板

## 适用场景

当用户要求“按顺序落地”“给实现计划”“说明要改哪些文件”时读取本文件。实现计划必须先说明层级、文件职责和验证方式，再进入编码。

如果实现计划包含鉴权、防篡改、集群路由、统一响应或压测验收，必须同步读取对应 reference：

- 鉴权、防篡改：`signature-canonicalization.md`
- 集群路由：`cluster-routing.md`
- 统一响应：`response-contract.md`
- 压测验收：`observability-testing.md`

## 模板

````markdown
# Netty Handler Dispatcher 实现计划

## 改动层级

- Transport：
- Protocol Parser：
- Auth/Signature：
- Router/Registry：
- Handler：
- Service：
- Response Writer：
- Observability：

## 文件职责

| 文件 | 新增/修改 | 职责 | 禁止承载 |
| --- | --- | --- | --- |
| `transport/websocket/HttpUpgradeAuthHandler.java` | 新增/修改 | WebSocket Upgrade 阶段鉴权、签名和重放校验 | 业务规则、数据库访问 |
| `transport/websocket/WsAuthMessageHandler.java` | 新增/修改 | `auth-message` 模式首条 AUTH 校验 | 普通业务 func |
| `transport/tcp/TcpFrameDecoder.java` | 新增/修改 | TCP 拆包/粘包和最大帧长度校验 | 鉴权、业务规则 |
| `transport/tcp/TcpAuthHandler.java` | 新增/修改 | TCP 建连后首条 `AUTH` 的认证窗口、签名和重放校验，认证成功后放行业务 func | 普通业务 func 处理 |
| `transport/udp/UdpDatagramDecoder.java` | 新增/修改 | UDP datagram 解码、大小限制和基础字段校验 | 重业务处理 |
| `protocol/MessageEnvelope.java` | 新增/修改 | 请求/通知 `reqid/func/version/ts/traceId/payload` envelope；有序 UDP/TCP/WebSocket 业务可在 payload 内使用 `seqno`；不作为响应 DTO | 网络连接对象、transport 专属安全字段、响应 JSON 字段 |
| `protocol/HttpHeaderSecurityFields.java` | 新增/修改 | HTTP/REST 或 WebSocket Upgrade Header 安全字段解析；CMS HTTP/REST 解析 `authorization/x-udid/x-reqid/x-timestamp/x-sign/x-sign-alg/x-api-version` 且不要求 `x-api-key`，SDK/OpenAPI 与 WebSocket `signed-upgrade` 解析 `authorization/x-reqid/x-timestamp/x-sign/x-sign-alg/x-api-version/x-api-key`，并按公开探活、CMS 受保护接口、SDK/OpenAPI 高风险请求和 signed-upgrade 分别校验必填性 | TCP/UDP/WebSocket 消息 envelope 解析、业务鉴权 |
| `protocol/MessageSecurityEnvelopeFields.java` | 新增/修改 | WebSocket 首条 `AUTH`、TCP `AUTH`、TCP/UDP 高风险消息和已认证 WebSocket 高风险业务消息的 envelope 顶层 `sign/sign-alg/api-key` 字段解析，按 `func` 风险等级或认证阶段校验消息级签名必填性 | HTTP Header 解析、`udid` 或 `authorization` 主体解析 |
| `protocol/TcpUdpSecurityEnvelopeFields.java` | 新增/修改 | TCP/UDP envelope 顶层 `udid/authorization` 字段解析，并按匿名公开探测、已识别设备请求、高风险请求分别校验必填性；消息级 `sign/sign-alg/api-key` 交给 `MessageSecurityEnvelopeFields` | WebSocket HTTP Header 解析、已认证 WebSocket 业务消息字段解析 |
| `security/canonical/*CanonicalBuilder.java` | 新增/修改 | 按入口构造 canonical request：HTTP、WebSocket Upgrade、WebSocket AUTH、WebSocket 高风险业务消息、TCP AUTH、TCP/UDP 高风险消息分别独立 builder；`CanonicalRequest` 必须包含 `UDID/KEY_ID/SIGN_ALG` 槽位 | 读取密钥、比较签名、业务鉴权 |
| `security/AuthContextResolver.java` | 新增/修改 | 将 token、短期票据或设备凭据解析为认证主体和授权上下文，供 WebSocket AUTH、TCP AUTH 或 HTTP/Upgrade 复用 | WebSocket transport 生命周期、具体业务规则 |
| `security/SignatureVerifier.java` | 新增/修改 | 接收 canonical request、按入口使用 `x-api-key/api-key` 或 CMS 登录主体/token 指纹定位验签材料、校验 `sign-alg` 白名单并比较签名 | 构造不同入口的 canonical string、HTTP/Netty 写回 |
| `security/ReplayKeyResolver.java` | 新增/修改 | 按入口从已解析安全字段构造 replay key；具体 replay key 形状以 `signature-canonicalization.md` 的防重放规则为准 | 签名比较、TTL 缓存存取、业务幂等结果、重新定义 replay key 形状 |
| `security/ReplayCache.java` | 新增/修改 | 接收 `ReplayKeyResolver` 输出的 replay key 做短 TTL 去重，可保存脱敏传输响应摘要，返回重复请求的已处理摘要或重放拒绝 | 构造 replay key、重拼 canonical string、业务幂等结果、业务结果持久化、模糊连接身份去重 |
| `observability/SecurityEventLogger.java` | 新增/修改 | 记录鉴权、签名、重放和时间戳安全事件；字段使用有限枚举 `securityStage/signAlg/canonicalBuilder/contentTypeClass/bodyHashSource/replayKeyType`，HTTP/REST 需区分 GET query、POST JSON raw body、CMS form raw body 来源 | 记录完整签名、完整 replay key、token、`api-key` 原值、完整 `Content-Type`、body 原文或 body hash 原值 |
| `observability/NettyMetricsBinder.java` | 新增/修改 | 发布 `netty_signature_verify_total`、`netty_signature_verify_duration_ms`、`netty_signature_fail_total`、`netty_replay_rejected_total`、`netty_timestamp_skew_rejected_total` 等安全指标；签名失败标签包含 `transport/nodeId/stage/reason/signAlg/canonicalBuilder/bodyHashSource/contentTypeClass`，正常验签耗时标签只用有限枚举 | 使用 `reqid/connectionId/userId/udid/IP/bodyHash` 等高基数字段做指标标签 |
| `router/MessageHandlerRegistry.java` | 新增/修改 | `func + version` 到 handler 的显式注册和重复 key 校验 | 字符串拼接 bean 名 |
| `handler/*Handler.java` | 新增/修改 | 消息级 DTO 适配并调用 service | 完整业务流程 |
| `service/*ApplicationService.java` | 复用/修改 | 核心业务规则和状态编排 | Netty Channel 依赖 |
| `writer/NettyResponseWriter.java` | 新增/修改 | 按 `response-contract.md` 统一响应、ACK、错误码映射和日志脱敏；响应和 ACK 只写 `reqid/code/message/ts/data`，禁止顶层 `func/version/traceId/status` | 业务判断、协议专属分支膨胀 |

## 验证

- 单元测试：覆盖 `MessageHandlerRegistry` 重复 key、`NettyResponseWriter` 统一响应字段、各入口 `CanonicalBuilder` 字段顺序和 `SignatureVerifier` 不构造 canonical string。
- 集成测试：覆盖 HTTP、Netty UDP、Netty TCP、Netty WebSocket 入口复用同一核心 service，响应保持 `reqid/code/message/ts/data`。
- 安全测试：覆盖重放攻击、签名错误、时间戳超窗、消息过大、敏感日志检查；HTTP/REST 必须覆盖 GET query 排序、POST `application/json` 原始 body hash、CMS POST `application/x-www-form-urlencoded` 原始表单 body hash，并验证 `canonicalBuilder/bodyHashSource/contentTypeClass` 日志字段、`netty_signature_verify_total`、`netty_signature_verify_duration_ms` 和 `netty_signature_fail_total` 标签。
- 压测指标：覆盖 `netty_message_latency_ms`、`netty_signature_verify_duration_ms`、`netty_signature_fail_total`、`netty_replay_rejected_total`、`netty_timestamp_skew_rejected_total`、`netty_udp_datagrams_dropped_total` 和 EventLoop 阻塞指标。
- 回滚验证：关闭新增签名/路由策略后，旧 HTTP/UDP/TCP 入口和新 Netty UDP/TCP/WebSocket 入口能按灰度规则回退。
````
