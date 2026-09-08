# 统一响应契约

## 响应 JSON

参考 `java-backend-api-standard` 的统一 API 契约，Netty handler 响应也应使用统一结构：

```json
{
  "reqid": "same-as-request",
  "code": "000000",
  "message": "成功",
  "ts": 1720000000123,
  "data": {}
}
```

规则：

- 成功响应：`code` 固定使用字符串 `000000`，`message` 使用成功文案，`data` 返回业务数据对象。
- 失败响应：`code` 必须使用稳定错误码字符串，例如 `AC0001`；禁止在响应 `code` 中返回英文枚举名，`message` 返回具体错误信息，`data` 返回 `null`。
- 不返回单独的 `status` 字段；`code=000000` 已经代表成功，非 `000000` 已经代表失败，额外 `status` 会造成语义重复或与 `code` 冲突。
- 禁止的是响应或 ACK 顶层协议状态字段；请求/通知 `payload` 或响应 `data` 内部可以按业务需要包含领域状态字段，但不得用它替代统一 `code`。
- `reqid` 为必填字段；正常响应必须原样回传请求 `reqid`。无法解析请求或服务端主动响应时，服务端生成新的唯一 `reqid`。
- `ts` 为必填字段；使用服务端生成的 Unix 时间戳（毫秒），表示响应生成时间，不回传客户端请求时间。
- `code` 和 `message` 应一一对应；错误语义写在 `message`，不要把语义塞进 `code`。

## ACK JSON

ACK 属于响应类消息，使用与普通响应相同的 `reqid/code/message/ts/data` 结构，不返回顶层 `func`、`version`、`traceId` 或 `status`。

```json
{
  "reqid": "same-as-notify-or-request",
  "code": "000000",
  "message": "已接收",
  "ts": 1720000000300,
  "data": {
    "ackFunc": "TOKEN_STATUS_NOTIFY",
    "ackStatus": "RECEIVED"
  }
}
```

规则：

- ACK 的 `reqid` 必须回传被确认的请求或通知 `reqid`；无法确认来源时，服务端生成新的唯一 `reqid` 并在日志记录原因。
- ACK 的 `code` 和普通成功响应一致，成功固定为字符串 `000000`；失败 ACK 使用稳定错误码字符串。
- ACK 的 `message` 使用中文提示，例如 `已接收`、`已拒绝`；机器枚举值放在 `data.ackStatus`，不要把 `message` 写成 `RECEIVED` 这类英文状态。
- ACK 如需说明确认对象，放在 `data.ackFunc`；如需说明确认状态，放在 `data.ackStatus`。
- ACK 不作为入站业务 `func + version` 注册 handler；入站 ACK 由协议层或统一 writer/dispatcher 边界处理。

## 错误码规则

失败 `code` 使用 6 位字符串，格式为 `SMEEEE`：

- `S`：1 位大写字母，代表某个系统，例如 `A`、`B`。
- `M`：1 位大写字母，代表该系统下的某个模块，例如 `C` 表示公共模块、`U` 表示用户模块、`P` 表示支付模块。
- `EEEE`：4 位数字，代表错误编号，从 `0001` 开始分配，保留 `9999` 作为系统或模块兜底错误。

示例：

- `AC0001`：系统 `A` 公共模块参数错误。
- `AC9999`：系统 `A` 公共兜底错误。
- `BU0001`：系统 `B` 用户模块错误 `0001`。

错误码表达的是协议拒绝或业务失败，不等同于 Java 异常：

- 鉴权失败、签名失败、重放请求、参数错误、资源不存在、状态不允许、限流命中和幂等冲突等可预期失败，返回稳定错误码和统一响应/ACK，不作为异常控制流。
- 程序缺陷、依赖异常、协议解析器缺陷、ACK/响应写出失败等不可预期问题，才进入异常处理链，并按观测标准使用 `log.error` 脱敏记录；客户端协议格式错误、字段格式错误和 JSON 解析失败按可预期协议拒绝处理，返回稳定错误码并使用结构化 info 日志和指标观察。

## 字段边界

- `traceId` 仅用于服务端日志和内部链路追踪，不作为响应 JSON 字段返回。
- 响应 JSON 不返回 `func`；请求和通知中的 `func + version` 只用于路由和统计。
- 响应 JSON 不返回顶层 `status`；业务 `payload` 或 `data` 里的订单状态、设备状态、令牌状态等领域字段可以存在，但必须保持在业务对象内部。
- 需要请求响应匹配时使用 `reqid`，不要把 `func` 放回响应体；客户端可用 `ts` 进行时钟偏差和端到端延迟排查。
- ACK 和普通响应一样不返回顶层 `func`、`version`、`traceId` 或 `status`；确认对象和机器状态放在 `data.ackFunc`、`data.ackStatus`。
