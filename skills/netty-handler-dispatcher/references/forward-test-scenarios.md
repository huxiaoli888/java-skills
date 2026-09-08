# Forward-test 场景

## 目录

- [场景一：TCP 与 UDP 高风险消息签名](#场景一tcp-与-udp-高风险消息签名)
- [场景二：WebSocket 鉴权模式选择](#场景二websocket-鉴权模式选择)
- [场景三：响应与 ACK 字段边界](#场景三响应与-ack-字段边界)

本文件用于维护 `netty-handler-dispatcher` 后做前向验证。普通 Netty 设计、评审或实现任务不需要默认读取。

## 场景一：TCP 与 UDP 高风险消息签名

输入任务：

```text
请设计 TCP 和 UDP 设备上报协议。
设备已识别，消息需要鉴权、防篡改、防重放，并且部分业务消息需要顺序语义。
```

预期关注点：

- envelope 顶层使用 `reqid/ts/api-key/sign/sign-alg/version/func/payload`。
- 设备或用户唯一标识使用顶层 `udid`。
- 有顺序语义的低风险业务字段使用 `payload.seqno`，字段名为 `seqno`。
- `reqid` 用于幂等、去重和请求追踪，不能替代业务顺序号。
- 签名原文包含 `reqid + ts + api-key + udid + sign-alg + func + version + payloadHash`。

### Input Sample

```json
{
  "reqid": "r-1",
  "ts": 1720000000123,
  "version": "V1",
  "func": "TOKEN_UPLOAD",
  "payload": { "sequenceNo": 1 }
}
```

### Expected Findings

- rule: tcp-udp-security-envelope
  keyword: 高风险或已识别设备请求必须携带 udid/sign/sign-alg/api-key
- rule: seqno-contract
  keyword: 业务顺序字段应使用 payload.seqno，不能继续使用 sequenceNo

## 场景二：WebSocket 鉴权模式选择

输入任务：

```text
请评估一个 WebSocket 长连接认证方案，客户端不能稳定在 Upgrade 阶段携带完整签名头。
```

预期关注点：

- 不强行要求所有 WebSocket 都使用 signed upgrade。
- 可以选择 `auth-message`，首条 `AUTH` 消息带签名 envelope。
- Upgrade 阶段仍需要 path、Origin、短期票据和基础限流。
- 认证超时必须关闭连接，不能允许未认证连接进入业务 handler。

### Input Sample

```json
{
  "func": "TOKEN_UPLOAD",
  "version": "V1",
  "reqid": "r-2",
  "payload": {
    "sign": "signature",
    "sign-alg": "HMAC-SHA256",
    "api-key": "key-id"
  }
}
```

### Expected Findings

- rule: websocket-auth-message
  keyword: 客户端不能稳定携带 Upgrade 签名头时使用首条 AUTH 消息
- rule: websocket-unauthenticated-close
  keyword: 认证超时必须关闭连接

## 场景三：响应与 ACK 字段边界

输入任务：

```text
请生成 Netty TCP/UDP/WebSocket 的统一响应和 ACK 设计。
```

预期关注点：

- 响应和 ACK 顶层统一使用 `reqid/code/message/ts/data`。
- 成功固定 `code=000000`，失败使用 `SMEEEE` 格式。
- ACK 不是入站业务 handler，不注册 `ACK + V1`。
- 业务状态只能放在 `data` 或 `payload` 内，不把业务状态字段提升为协议顶层。

### Input Sample

```json
{
  "reqid": "r-3",
  "status": "SUCCESS",
  "code": "AC0001",
  "message": "RECEIVED",
  "func": "ACK",
  "data": {}
}
```

### Expected Findings

- rule: response-contract-boundary
  keyword: 响应和 ACK 顶层统一使用 reqid/code/message/ts/data
- rule: ack-registration-boundary
  keyword: ACK 不是入站业务 handler，不注册 ACK + V1
