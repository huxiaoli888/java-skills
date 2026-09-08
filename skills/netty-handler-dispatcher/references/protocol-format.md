# 协议格式与消息分发规则




## 目录

- [统一架构](#统一架构)
- [UDP/TCP 快速规则](#udptcp-快速规则)
- [TCP/WebSocket 长连接规则](#tcpwebsocket-长连接规则)
- [Envelope](#envelope)
- [错误码规则](#错误码规则)
- [Func 命名和版本](#func-命名和版本)
- [生命周期](#生命周期)
- [幂等顺序重试超时](#幂等顺序重试超时)
- [安全与限流](#安全与限流)
- [协议格式选择](#协议格式选择)

## 统一架构

```text
传输入口
  -> 连接/报文接收
  -> 协议解析
  -> func + version 识别
  -> handler 分发
  -> DTO 转换
  -> 业务 service
  -> 状态更新 / MQ / 外部调用
  -> 统一响应 / ACK / 错误码 / 日志
```

## UDP/TCP 快速规则

- UDP/TCP 与 WebSocket 一样使用统一 envelope、`func + version + reqid` 和 handler registry，不按业务动作拆端口或连接。
- TCP 必须显式处理拆包/粘包；UDP 必须显式处理丢包、乱序、重复和 datagram 大小。
- TCP/UDP 的详细 pipeline、ACK、重试、幂等、签名和 I/O 线程边界见 `references/netty-tcp-udp.md`。

## TCP/WebSocket 长连接规则

Netty TCP / Netty WebSocket 用一个业务域长连接承载多种消息，通过统一 envelope 的 `func + version + reqid` 分发 handler。

推荐 endpoint：

```text
/ws/mss
/ws/token
/ws/device
```

不推荐：

```text
/ws/token/upload
/ws/token/down
/ws/token/upload/v2
```

## Envelope

TCP/UDP 高风险请求：

```json
{
  "reqid": "client-generated-id",
  "func": "TOKEN_UPLOAD",
  "version": "V2",
  "ts": 1720000000000,
  "traceId": "optional-trace-id",
  "udid": "device-or-user-id",
  "authorization": "Bearer token",
  "sign": "signature",
  "sign-alg": "HMAC-SHA256",
  "api-key": "key-id",
  "payload": {}
}
```

WebSocket 已认证连接上的低风险业务请求：

```json
{
  "reqid": "client-generated-id",
  "func": "DEVICE_PING",
  "version": "V1",
  "ts": 1720000000000,
  "traceId": "optional-trace-id",
  "payload": {}
}
```

WebSocket 已认证连接上的高风险业务请求：

```json
{
  "reqid": "client-generated-id",
  "func": "TOKEN_UPLOAD",
  "version": "V2",
  "ts": 1720000000000,
  "traceId": "optional-trace-id",
  "sign": "signature",
  "sign-alg": "HMAC-SHA256",
  "api-key": "key-id",
  "payload": {}
}
```

`TOKEN_UPLOAD` 属于高风险业务示例。TCP/UDP 示例必须携带 `udid/authorization/sign/sign-alg/api-key`。WebSocket 的握手签名使用 HTTP Header `x-reqid/x-timestamp/x-sign/x-sign-alg/x-api-version/x-api-key`；握手后的低风险业务消息可依赖已认证连接，高风险业务消息必须按消息级签名规则在 envelope 顶层携带 `sign/sign-alg/api-key`。具体签名原文和 replay key 形状以 `signature-canonicalization.md` 为准，不要把 HTTP `x-*` Header 字段放入 `payload`。

服务端通知：

```json
{
  "reqid": "server-generated-id",
  "func": "TOKEN_STATUS_NOTIFY",
  "version": "V1",
  "ts": 1720000000200,
  "payload": {}
}
```

响应与 ACK 的完整 JSON 示例、字段语义、错误码格式和 ACK `data.ackFunc/data.ackStatus` 规则见 `response-contract.md`；本文件只保留字段矩阵，避免双写响应契约。

字段规则：

| 字段 | 请求 | 响应 | 通知 | ACK | 说明 |
| --- | --- | --- | --- | --- | --- |
| `reqid` | 必填 | 必填 | 必填 | 必填 | 请求响应匹配、幂等、排障 |
| `func` | 必填 | 禁止 | 必填 | 禁止 | 消息功能；响应类消息不返回 |
| `version` | 必填 | 禁止 | 必填 | 禁止 | 协议版本；响应类消息不返回 |
| `ts` | 高风险、签名或防重放请求必填；低风险请求建议 | 必填 | 必填 | 必填 | Unix 时间戳（毫秒）；请求侧用于重放窗口校验，响应/ACK 使用服务端生成时间，用于延迟与时钟偏差排查 |
| `traceId` | 建议 | 禁止 | 建议 | 禁止 | 请求/通知可选；服务端记录内部链路追踪，不向响应类报文返回 |
| `udid` | TCP/UDP 高风险或已识别设备请求必填，匿名公开探测可省略；WebSocket 普通业务默认禁止 | 禁止 | 禁止 | 禁止 | TCP/UDP 请求的设备或用户唯一标识；登录前代表设备，登录后可代表用户或设备；WebSocket 连接身份来自握手或首条 `AUTH` |
| `authorization` | TCP/UDP 按需；WebSocket 首条 `AUTH` 按需 | 禁止 | 禁止 | 禁止 | 登录后的 token；公开探测、探活类请求可豁免 |
| `sign` | TCP/UDP 高风险必填；WebSocket 高风险业务消息级签名必填，低风险可省略 | 禁止 | 禁止 | 禁止 | 消息级签名结果；WebSocket Upgrade 仍使用 HTTP Header `x-sign` |
| `sign-alg` | TCP/UDP 高风险必填；WebSocket 高风险业务消息级签名必填，低风险可省略 | 禁止 | 禁止 | 禁止 | 消息级签名算法，例如 `HMAC-SHA256` |
| `api-key` | TCP/UDP 高风险必填；WebSocket 高风险业务消息级签名必填，低风险可省略 | 禁止 | 禁止 | 禁止 | 消息级密钥标识，用于定位验签密钥，不是密钥本身 |
| `payload` | 必填 | 禁止 | 必填 | 禁止 | 请求/通知业务负载 |
| `code` | 禁止 | 必填 | 禁止 | 必填 | 统一错误码字符串；成功 `000000`，失败使用 `SMEEEE` 格式 |
| `message` | 禁止 | 必填 | 禁止 | 必填 | 排障或客户端提示 |
| `data` | 禁止 | 必填 | 禁止 | 必填 | 成功返回业务数据，失败返回 `null`；ACK 可放 `ackFunc`、`ackStatus` 等确认详情 |

## 错误码规则

完整响应 JSON、ACK 和错误码契约以 `response-contract.md` 为准；本节只记录协议层必须遵守的摘要边界：

- `code` 必须用字符串承载，成功固定为 `000000`，失败使用 `SMEEEE` 格式稳定错误码，避免前导零丢失，并保持 HTTP、UDP、TCP、WebSocket 四类入口含义一致。
- 响应和 ACK 顶层字段只允许 `reqid/code/message/ts/data`，禁止把 `func/version/traceId/status` 放回响应类报文。
- 正常协议拒绝和业务失败使用错误码表达，不通过异常推进流程；真正程序异常不能吞掉，按 `observability-testing.md` 使用 `log.error` 脱敏记录。
- 具体 `reqid` 回传、服务端生成 `ts`、`message` 文案、ACK data 字段和错误码分配规则只看 `response-contract.md`。

## Func 命名和版本

- `func` 使用大写下划线：`TOKEN_UPLOAD`、`TOKEN_DOWN`、`HEARTBEAT`。
- 按业务域前缀聚合：`TOKEN_*`、`CHARGE_*`、`DEVICE_*`、`SESSION_*`。
- 请求和通知使用 `func` 路由；响应 JSON 不返回 `func` 或 `traceId`，通过 `reqid + code/message/data + ts` 表达结果。
- 服务端主动推送使用 `_NOTIFY` 后缀。
- ACK 属于响应类消息，不返回 `func`；如需说明确认的通知类型和状态，在 `data.ackFunc`、`data.ackStatus` 中记录。
- 心跳使用 `HEARTBEAT`，不要复用业务 func。
- 不要把版本写进 func 名称，版本放到 `version`。
- `version` 使用 `V1`、`V2`、`V3` 这类稳定字符串。
- 删除字段、改变字段语义、改变错误码含义时必须升版本。
- 同一个 `func + version` 的语义必须不可变。

## 生命周期

```text
CONNECT
  -> AUTHENTICATING
  -> AUTHENTICATED
  -> ACTIVE
  -> IDLE
  -> CLOSING
  -> CLOSED
```

规则：

- 建连后必须在限定时间内完成鉴权，超时关闭。
- 鉴权失败返回错误并关闭，不进入业务 handler。
- 重复登录策略要明确：允许多端、踢旧连接或拒绝新连接。
- 心跳超时进入 `IDLE` 或直接关闭。
- 服务重启或连接断开后，客户端必须能用业务状态恢复，不依赖内存 session。

建议关闭码：

| 场景 | 建议码 |
| --- | --- |
| 正常关闭 | `1000` |
| 协议格式错误 | `1002` |
| 消息过大 | `1009` |
| 鉴权失败 | `4001` |
| 心跳超时 | `4002` |
| 重复登录被踢 | `4003` |
| 服务端过载 | `4500` |

## 幂等顺序重试超时

- `reqid` 在需要防重放或幂等的范围内必须唯一：连接型协议按连接或已认证主体约束，HTTP/UDP 按 replay key 或业务幂等维度约束。
- 关键业务还应使用业务幂等键，如 `seqno`、`tokenIndex`、`orderNo`。
- 服务端应在短 TTL 内缓存已处理 `reqid` 的传输响应摘要，用于重复请求快速返回或拒绝重放。
- 业务幂等结果必须由 service 层按业务键持久化或可靠存储，不能放进 `ReplayCache`。
- 默认不保证跨 `func` 全局有序。
- 需要顺序时在 payload 中增加 `seqno` 或业务流水。
- 客户端只对 `retryable=true` 或网络断开场景重试。
- 参数错误、鉴权失败、版本不支持不应重试。
- 业务 handler 超时后返回统一错误，不让连接无限等待。

## 安全与限流

- 未鉴权连接禁止进入业务 handler。
- 长连接也必须有鉴权和防篡改设计，不能因为连接已建立就默认信任后续消息。
- WebSocket 握手仍使用 HTTP Header：`authorization`、`x-reqid`、`x-timestamp`、`x-sign`、`x-sign-alg`、`x-api-version`、`x-api-key`；历史项目如已有 `appKey/keyId`，只能作为兼容别名，不作为新协议推荐字段。公开探活、握手探测类接口可配置豁免，但不得进入业务 handler。
- TCP 首条 `AUTH` 和 UDP 高风险请求使用 envelope 顶层字段：`udid`、`authorization`、`sign`、`sign-alg`、`api-key`，并复用 `reqid`、`ts`、`version`；匿名公开探测可省略 `udid` 和签名材料，但必须限流；不要在 TCP/UDP payload 中重复放 `x-reqid`、`x-timestamp`、`x-api-version`。
- `authorization` 只承载登录后的 token；`sign` 或 `x-sign` 承载签名结果；`sign-alg` 或 `x-sign-alg` 承载签名算法；`api-key` 或 `x-api-key` 用于定位验签密钥，不是密钥本身。
- `reqid` 或 `x-reqid` 由客户端生成，在重放窗口内唯一；服务端必须按入口类型构造 replay key，具体 replay key 形状、防重放维度、短期票据优先级和 `connectionId` 兜底规则以 `signature-canonicalization.md` 为准。
- WebSocket 首条 `AUTH` 如果使用短期票据，票据必须单次使用并参与防重放维度；已认证 WebSocket 高风险业务消息优先使用已认证主体做重放维度，`connectionId` 只能作为兜底。具体 key 形状只在 `signature-canonicalization.md` 维护。
- `ts` 或 `x-timestamp` 用于校验请求时间窗口，默认允许偏差 `300s`，具体项目可按安全等级收紧。
- 握手或消息签名原文必须明确且稳定；固定字段槽位、`UDID/KEY_ID/SIGN_ALG` 含义、query 排序、body hash 来源、空 body hash 和 WebSocket 空 `UDID` 槽位都以 `signature-canonicalization.md` 为准。
- HTTP/REST CMS/SDK 签名必须覆盖 GET、POST `application/json` 和 CMS POST `application/x-www-form-urlencoded`；query/body hash 具体来源以 `signature-canonicalization.md` 为准，不在本文件重复定义。
- 消息级签名按 `func` 风险等级启用：交易、令牌、设备绑定、状态变更、敏感查询必须签名；TCP/WebSocket 已认证连接上的 `HEARTBEAT`、`ACK`、低风险服务端通知可依赖连接认证和 `reqid`。只有具备业务顺序语义的消息才在 `payload.seqno` 中使用顺序号，`seqno` 不替代 `reqid` 或 replay key。UDP 没有可靠连接态；UDP 高风险请求仍必须逐条携带鉴权和签名材料，匿名公开低风险 UDP 探测只能依赖限流和风控。
- TCP/UDP 高风险业务消息和 WebSocket 高风险业务消息都必须走对应 canonical builder；具体签名字段顺序、payload/frame bytes 选择和算法槽位绑定规则只在 `signature-canonicalization.md` 维护。
- 需要落地签名时，必须读取 `references/signature-canonicalization.md`，按其中固定字段顺序、query 排序、body hash 和防重放规则生成签名原文。
- 设置单消息最大字节数。
- 按 IP、账号、设备、连接、`func` 维度限流。
- 限制单 IP、单账号、单设备最大连接数。
- token、credential、手机号、身份证号、密钥材料不记录明文。
- 不同 `func` 必须可配置授权范围。

限流、服务繁忙、鉴权失败等响应体示例不要在本文件维护；写协议说明或实现时按 `response-contract.md` 和 `writer/NettyResponseWriter.java` 的映射输出。

## 协议格式选择

默认首选 JSON，除非消息体积、吞吐、带宽或兼容性要求证明需要二进制协议。

| 协议格式 | 适用场景 | 优点 | 缺点 | 推荐级别 |
| --- | --- | --- | --- | --- |
| JSON Text Frame | 管理端、SDK 初期、字段变化频繁 | 可读、易调试 | 体积大、序列化成本高 | 默认首选 |
| Protobuf Binary Frame | 高频消息、移动端省流量、协议稳定 | 体积小、速度快 | 需要 schema 管理 | 高性能场景推荐 |
| MessagePack / CBOR | 需要二进制但不想维护 IDL | 比 JSON 小 | 生态和可读性一般 | 可选 |
| ASN.1 / DER | 复用既有安全协议 | 严谨 | 开发和排障成本高 | 仅兼容既有协议 |
| 自定义 byte[] | 极致性能或硬件协议 | 最小体积 | 维护成本最高 | 谨慎使用 |

可选扩展字段：

```json
{
  "reqid": "client-generated-id",
  "func": "DEVICE_PING",
  "version": "V1",
  "contentType": "application/json",
  "ts": 1720000000000,
  "udid": "device-or-user-id",
  "payload": {}
}
```
