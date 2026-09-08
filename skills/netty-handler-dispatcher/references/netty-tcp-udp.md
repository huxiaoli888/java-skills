# Netty TCP/UDP 设计规则




## 目录

- [TCP 规则](#tcp-规则)
- [UDP 规则](#udp-规则)
- [I/O 线程边界](#io-线程边界)
- [验收清单](#验收清单)

## TCP 规则

### 编解码与拆包

- TCP 必须显式处理粘包和半包，不允许直接把一次 `channelRead` 当作一条完整业务消息。
- JSON 协议建议使用长度字段封帧：`length + envelopeJson`。
- 二进制协议建议使用 `LengthFieldBasedFrameDecoder` 和 `LengthFieldPrepender`。
- 单帧最大长度必须配置化，默认建议 `64KB` 起步；超过上限产生帧过大失败并交给统一 writer 映射，或关闭连接。
- 协议解析失败、未知 `func + version` 都必须抛出类型化失败，由 `writer/NettyResponseWriter.java` 按 `response-contract.md` 映射最终 `code`。

本文件不定义具体 `AC000x` 错误码；TCP/UDP transport 只产生类型化失败原因，最终响应 `reqid/code/message/ts/data` 由 `writer/NettyResponseWriter.java` 统一写出。

推荐 pipeline：

```text
ServerBootstrap
  -> LengthFieldBasedFrameDecoder
  -> LengthFieldPrepender
  -> ProtocolMessageDecoder
  -> IdleStateHandler
  -> TcpAuthHandler
  -> TcpMessageDispatcher
  -> writer/NettyResponseWriter
```

### TCP/UDP 基础配置清单

实现 TCP/UDP 入口时，以下参数必须配置化，不要散落硬编码在 handler 中：

| 参数 | 建议默认值 | 说明 |
| --- | --- | --- |
| `tcp.max-frame-bytes` | `65536` | TCP 单帧最大长度，超过上限产生帧过大失败或关闭连接 |
| `tcp.auth-timeout-ms` | `10000` | 建连后首条 `AUTH` 认证窗口 |
| `tcp.reader-idle-seconds` | `90` | TCP 心跳或读空闲超时 |
| `udp.max-datagram-bytes` | `1400` 或按网络 MTU 评估 | UDP 单个 datagram 最大业务负载 |
| `udp.route-ttl-seconds` | `30~120` | UDP 上层 route 或异步响应 endpoint 短 TTL |
| `security.timestamp-skew-seconds` | `300` | `ts` 与服务端时间允许偏差 |
| `security.replay-ttl-seconds` | `300` | `reqid` replay key 短 TTL 去重窗口 |
| `rate-limit.max-qps-per-udid` | 按业务压测确定 | 设备或用户维度限流 |

### TCP envelope

TCP 基础 envelope 使用 `reqid + func + version + ts + payload`，不要按不同动作拆连接或端口。高风险请求、已识别设备请求或需要设备维度防重放的请求再携带 `udid`；需要鉴权或签名的 TCP 请求，把安全字段放在 envelope 顶层，不要塞进 `payload`。

```json
{
  "reqid": "client-generated-id",
  "func": "TOKEN_UPLOAD",
  "version": "V2",
  "ts": 1720000000000,
  "udid": "device-or-user-id",
  "authorization": "Bearer token",
  "sign": "signature",
  "sign-alg": "HMAC-SHA256",
  "api-key": "key-id",
  "payload": {}
}
```

### TCP 鉴权与防篡改

- TCP 建连后必须在 `auth-timeout-ms` 内完成首条 `AUTH` 消息认证。
- `AUTH` envelope 顶层应包含 `authorization`、`sign`、`sign-alg`、`api-key`；复用 envelope 已有的 `reqid`、`ts`、`version`，不要再额外放 `x-reqid`、`x-timestamp`、`x-api-version`。
- 认证前只允许 `AUTH`、底层 ping 或握手探测；其他 `func` 产生认证失败响应并关闭连接，具体错误码由统一 writer 映射。
- 高风险业务消息按 `func` 启用消息级签名，签名原文包含 `reqid + ts + udid + api-key + sign-alg + func + version + payloadHash`，算法标识必须绑定进签名原文。
- `udid` 表示设备或用户唯一标识；登录前可代表设备，登录后可代表用户或设备。
- `reqid` 在重放窗口内唯一，服务端必须按入口类型构造 replay key；TCP `AUTH` 或高风险业务消息使用 `tcp:{api-key}:{reqid}:{udid}` 做短 TTL 去重，不使用模糊连接身份替代 `api-key + reqid + udid`。

TCP 首条 `AUTH` 示例：

```json
{
  "reqid": "client-generated-id",
  "func": "AUTH",
  "version": "V1",
  "ts": 1720000000000,
  "udid": "device-or-user-id",
  "authorization": "Bearer token",
  "sign": "signature",
  "sign-alg": "HMAC-SHA256",
  "api-key": "key-id",
  "payload": {
    "clientType": "sdk"
  }
}
```

TCP `AUTH` 的签名原文按 `signature-canonicalization.md` 的业务消息 canonical string 执行，`FUNC=AUTH`，`BODY_SHA256_HEX` 使用首条 `AUTH` 原始消息体 bytes 或项目明确的 canonical payload bytes。认证成功后才允许 `TOKEN_UPLOAD`、`DEVICE_STATUS_REPORT` 等业务 `func` 进入 dispatcher。

### TCP 顺序、ACK 和重试

- 同一连接内读取顺序天然有序，但异步业务处理可能导致响应乱序；客户端必须用 `reqid` 匹配响应。
- 需要业务顺序时在 payload 内增加 `seqno`，服务端按业务键串行化或拒绝乱序。
- 关键通知使用 ACK，ACK 超时后重试；重试次数耗尽后转离线消息、MQ 死信或客户端主动查询兜底。
- 不要为了保持顺序阻塞 EventLoop。

## UDP 规则

### 报文边界

- UDP 单个 datagram 天然有边界，但可能丢包、乱序、重复。
- UDP payload 必须短小，避免超过路径 MTU；默认建议控制在 `1200 bytes` 内，除非有明确网络环境证明。
- 大 payload 不通过 UDP 直接传输，改为传对象引用、分片协议或升级 TCP/WebSocket。
- 新协议必须显式携带 `func + version + reqid + ts`；高风险请求、已识别设备请求或需要设备维度防重放的请求还必须携带 `udid`。

### UDP envelope

UDP 请求同样把鉴权、防篡改字段放在 envelope 顶层。匿名公开低风险探测可以省略 `udid/authorization/sign/sign-alg/api-key`，但必须限流；需要识别设备、鉴权或防篡改的请求必须携带 `udid`。`seqno` 只用于有业务顺序语义的请求，不是所有 UDP 请求必填。

匿名公开低风险 UDP 探测请求（无设备身份、可省略鉴权和签名字段，但必须限流）：

```json
{
  "reqid": "client-generated-id",
  "func": "PUBLIC_PING",
  "version": "V1",
  "ts": 1720000000000,
  "payload": {}
}
```

需要鉴权的 UDP 探测请求：

```json
{
  "reqid": "client-generated-id",
  "func": "DEVICE_PING",
  "version": "V1",
  "ts": 1720000000000,
  "udid": "device-or-user-id",
  "authorization": "Bearer token",
  "sign": "signature",
  "sign-alg": "HMAC-SHA256",
  "api-key": "key-id",
  "payload": {}
}
```

有顺序要求的 UDP 状态上报请求：

```json
{
  "reqid": "client-generated-id",
  "func": "DEVICE_STATUS_REPORT",
  "version": "V1",
  "ts": 1720000000000,
  "udid": "device-or-user-id",
  "seqno": 1001,
  "authorization": "Bearer token",
  "sign": "signature",
  "sign-alg": "HMAC-SHA256",
  "api-key": "key-id",
  "payload": {
    "status": "ONLINE"
  }
}
```

UDP 响应使用统一响应结构，完整 JSON 示例和字段语义以 `response-contract.md` 为准；本文件不维护响应体示例。

### UDP 鉴权、防篡改与防重放

- UDP 没有连接态，除非上层另有可靠 session，否则每条高风险请求都必须自带鉴权和签名材料。
- 公共低风险探测可以不要求 token、签名或 `udid`，但必须限流；如果携带 `udid`，只能作为设备维度限流或风控信号，不能替代签名鉴权。
- 需要鉴权的 UDP 请求应在 envelope 顶层携带 `authorization` 或设备凭据、`sign`、`sign-alg`、`api-key`，并复用 `reqid`、`ts`、`version`。
- 防重放必须依赖 `reqid + ts + api-key + udid` 和短 TTL 去重缓存；不能只靠客户端 IP 或 UDP source port。
- UDP 中不要记录明文 token、密钥、手机号、身份证号。

### UDP ACK、重试和幂等

- UDP 请求天然可能丢包，客户端重试必须带同一个 `reqid` 或业务幂等键。
- 服务端在短 TTL 内缓存已处理 `reqid` 的传输响应摘要，重复请求返回同一响应摘要或拒绝为重放。
- 业务幂等结果必须由 service 层按 `seqno`、订单号、令牌索引等业务键保存，不得塞进 `ReplayCache`。
- 需要顺序的业务必须带 `seqno`，服务端发现旧序号或重复序号时返回幂等结果或顺序/参数错误响应，具体错误码由统一 writer 映射。
- 只允许客户端对 retryable 错误、超时或网络丢包重试；参数错误、鉴权失败和版本不支持不重试。

## I/O 线程边界

- TCP/UDP handler 只做收发、轻解析、基础校验和投递。
- Redis、MQ、DB、HTTP、磁盘日志、复杂签名验签必须放入业务线程池或异步链路。
- 业务线程池必须有有界队列和拒绝策略；拒绝时产生服务繁忙失败并交给统一 writer 映射，或丢弃低风险 UDP 请求。
- UDP 高峰场景要监控 socket receive buffer、丢包率、处理延迟和业务线程池队列。

## 验收清单

- TCP 已明确拆包/粘包方案和最大帧长度。
- UDP 已明确最大 datagram 大小、丢包、乱序和重复处理。
- TCP/UDP 都使用 `func + version + reqid` 分发。
- 高风险 TCP/UDP 消息有签名、防篡改和防重放规则。
- 响应错误码与 HTTP/WebSocket 保持 `000000 / SMEEEE` 一致，具体映射以 `response-contract.md` 为准。
- 慢操作不阻塞 Netty I/O 线程。
