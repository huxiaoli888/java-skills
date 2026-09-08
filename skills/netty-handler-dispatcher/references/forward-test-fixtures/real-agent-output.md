# Forward-test 真实子任务输出

> 来源：独立子任务使用 `netty-handler-dispatcher` 对 TCP/UDP 设备上报协议做评审。

## 协议评审/设计发现

1. 当前样例不满足安全要求：缺少 `udid`、`authorization` 或设备凭据、`sign`、`sign-alg`、`api-key`，只能表达业务意图，不能完成鉴权、防篡改、防重放。

2. TCP 和 UDP 不应按 `TOKEN_UPLOAD` 单独拆端口或连接。建议同一业务域统一入口，报文通过 `func + version + reqid` 分发到 handler，例如：
   - TCP：单业务域长连接，一个连接承载 `AUTH`、`HEARTBEAT`、`TOKEN_UPLOAD`、`DEVICE_STATUS_REPORT` 等。
   - UDP：单业务域端口，短请求短响应，每个 datagram 都显式携带 envelope。

3. 推荐统一请求 envelope：

```json
{
  "reqid": "r-1",
  "ts": 1720000000123,
  "version": "V1",
  "func": "TOKEN_UPLOAD",
  "udid": "device-001",
  "authorization": "Bearer token-or-device-credential",
  "api-key": "key-id",
  "sign-alg": "HMAC-SHA256",
  "sign": "base64-signature",
  "payload": {
    "seqno": 1
  }
}
```

4. `payload.sequenceNo` 建议改为 `payload.seqno`。`seqno` 只用于有业务顺序语义的消息，不替代 `reqid`，也不替代 replay key。无顺序要求的消息不要强行带序号。

5. TCP 鉴权建议：
   - 建连后 `tcp.auth-timeout-ms` 内必须发送首条 `AUTH`。
   - 未认证前只允许 `AUTH`、底层 ping 或探测消息。
   - 认证成功后业务消息进入 dispatcher。
   - 高风险消息如 `TOKEN_UPLOAD` 仍建议保留消息级签名，不能只依赖“连接已认证”。

6. UDP 鉴权建议：
   - UDP 无可靠连接态，高风险或已识别设备上报必须每条消息自带 `udid/authorization/sign/sign-alg/api-key/reqid/ts`。
   - 不允许仅凭 UDP source IP 或 source port 判断身份。
   - UDP 单 datagram 建议控制在 `1200` 字节以内，超过应改 TCP 或对象引用。

7. 防篡改签名原文建议固定为 canonical string，字段顺序稳定：
   - `METHOD/PATH/QUERY` 对 TCP/UDP 为空行。
   - 核心字段包含 `reqid`、`ts`、`udid`、`api-key`、`sign-alg`、`func`、`version`、`BODY_SHA256_HEX`。
   - `sign-alg` 必须参与签名，防止算法降级或替换。
   - `BODY_SHA256_HEX` 使用原始 payload/frame bytes 或项目明确的 canonical payload bytes，不能由服务端解析后随意重序列化。

8. 防重放建议：
   - 校验 `ts` 与服务端时间偏差，默认窗口 `300s`。
   - TCP replay key：`tcp:{api-key}:{reqid}:{udid}`。
   - UDP replay key：`udp:{api-key}:{reqid}:{udid}`。
   - replay cache 只保存短 TTL 传输响应摘要或重放标记，不保存业务幂等结果。
   - 同一 `reqid` 在窗口内重复出现，应返回原响应摘要或拒绝为重放。

9. 顺序语义建议：
   - 默认不保证跨 `func` 全局有序。
   - 对需要顺序的业务，按业务键维护 `lastSeqno`，例如 `udid + func` 或 `udid + tokenBatchId`。
   - `seqno == lastSeqno + 1`：正常处理。
   - `seqno <= lastSeqno`：返回幂等结果或重复序号响应。
   - `seqno > lastSeqno + 1`：返回乱序/缺口响应，客户端按策略重传或补偿。
   - 不要为了等前序消息而阻塞 Netty EventLoop。

10. 响应和 ACK 统一结构，不返回 `func/version/status/traceId`：

```json
{
  "reqid": "r-1",
  "code": "000000",
  "message": "成功",
  "data": {
    "retryable": false
  },
  "ts": 1720000000456
}
```

11. TCP 编解码必须显式处理粘包/半包，建议 `length + envelopeJson`，并配置 `tcp.max-frame-bytes`，默认可从 `65536` 起步。

12. 必须保留的治理项：
   - `tcp.auth-timeout-ms`
   - `tcp.reader-idle-seconds`
   - `udp.max-datagram-bytes`
   - `udp.route-ttl-seconds`
   - `security.timestamp-skew-seconds`
   - `security.replay-ttl-seconds`
   - `rate-limit.max-qps-per-udid`

13. Handler 分发建议使用显式 registry：`MessageKey(func, version) -> MessageHandler`。例如：
   - `AUTH + V1 -> AuthHandler`
   - `HEARTBEAT + V1 -> HeartbeatHandler`
   - `TOKEN_UPLOAD + V1 -> TokenUploadHandler`
   - `DEVICE_STATUS_REPORT + V1 -> DeviceStatusReportHandler`

14. 关键风险结论：当前输入样例可以作为业务 payload 雏形，但不能直接作为 TCP/UDP 设备上报协议投产。至少需要补齐顶层安全字段、固定签名原文、增加 replay cache、统一响应契约，并把 `sequenceNo` 规范为 `seqno` 后再进入 handler 设计。
