# Netty 传输签名 Canonicalization 规则




## 目录

- [适用范围](#适用范围)
- [字段来源](#字段来源)
- [Canonical String](#canonical-string)
- [按入口构造 Canonical Request](#按入口构造-canonical-request)
- [HTTP/REST 请求体与 Query 规则](#httprest-请求体与-query-规则)
- [JSON Payload Hash](#json-payload-hash)
- [算法建议](#算法建议)
- [防重放规则](#防重放规则)
- [示例](#示例)
- [验收清单](#验收清单)

## 适用范围

- WebSocket HTTP Upgrade 阶段的握手签名。
- TCP 首条 `AUTH` 消息签名。
- UDP 高风险请求签名。
- TCP/WebSocket 已认证连接上的高风险业务 `func` 消息级签名。

TCP/WebSocket 已认证连接上的 `HEARTBEAT`、`ACK`、低风险服务端通知可以依赖连接认证和 `reqid`，不强制每条消息签名。只有具备业务顺序语义的消息才在 `payload.seqno` 中使用顺序号，`seqno` 不替代 `reqid` 或 replay key。UDP 没有可靠连接态；UDP 高风险请求仍必须逐条携带鉴权和签名材料，匿名公开低风险 UDP 探测只能依赖限流和风控。

## 字段来源

| 语义 | HTTP/REST 或 WebSocket Upgrade Header | TCP/UDP/WebSocket 消息 Envelope 等价字段 | 说明 |
| --- | --- | --- | --- |
| 请求唯一编号 | `x-reqid` | `reqid` | 客户端生成，重放窗口内唯一；WebSocket `AUTH` 和高风险业务消息使用 envelope `reqid` |
| 时间戳 | `x-timestamp` | `ts` | Unix 毫秒时间戳；签名或防重放请求必填 |
| 设备或用户标识 | 无固定 Header，默认空字符串；如项目确需映射必须在项目 API 标准中另行定义 | TCP/UDP 使用 `udid`；WebSocket 消息无 `udid` 时使用空 `UDID` 槽位 | TCP/UDP 设备或用户唯一标识，参与重放缓存维度；WebSocket 业务消息不要伪造设备标识 |
| 签名结果 | `x-sign` | `sign` | Base64 或 hex，项目需固定一种 |
| 签名算法 | `x-sign-alg` | `sign-alg` | 例如 `HMAC-SHA256`、`RSA-SHA256` |
| 协议版本 | `x-api-version` | `version` | HTTP/REST 或 WebSocket Upgrade 使用 Header 契约版本；TCP/UDP/WebSocket 消息复用 envelope `version` |
| 密钥标识 | SDK/OpenAPI 与 WebSocket Upgrade 使用 `x-api-key`；CMS HTTP/REST 不使用 `x-api-key` | `api-key` | 用于定位验签密钥或公钥；不是密钥本身；CMS HTTP/REST 使用登录主体或 token 指纹作为调用身份；`x-app-key/appKey/keyId` 仅作为历史兼容别名 |
| 登录 token | `authorization` | `authorization` | 不直接参与签名时也必须参与鉴权；WebSocket 高风险业务消息的认证主体来自已认证连接上下文 |

## Canonical String

默认签名原文使用 UTF-8，字段顺序固定如下：

```text
METHOD
PATH
CANONICAL_QUERY
X_REQID
X_TIMESTAMP
UDID
KEY_ID
SIGN_ALG
FUNC
VERSION
BODY_SHA256_HEX
```

规则：

- 每个字段占一行，使用 `\n` 连接。
- 字段缺失时使用空字符串占位，不删除该行。
- `METHOD` 使用大写。WebSocket 握手使用 `GET`；TCP/UDP 无 HTTP method 时为空字符串。
- `PATH` 使用不含域名的 path，例如 `/ws/token`；TCP/UDP 无 path 时为空字符串。
- `CANONICAL_QUERY` 按 query 参数名升序排列，key/value 使用 RFC3986 百分号编码，格式为 `k1=v1&k2=v2`。没有 query 时为空字符串。
- `X_REQID` 使用 `x-reqid` 或 envelope `reqid` 的原始字符串。
- `X_TIMESTAMP` 使用 `x-timestamp` 或 envelope `ts` 的毫秒时间戳字符串。
- 参与签名或防重放的请求必须提供 `X_TIMESTAMP`，不得用空字符串绕过时间窗口校验。
- `UDID` 使用 envelope `udid` 的原始字符串；HTTP/REST 或 WebSocket Upgrade Header 没有等价字段时使用空字符串。
- `KEY_ID` 使用 `x-api-key` 或 envelope `api-key` 的原始字符串；CMS HTTP/REST 不使用 `x-api-key` 时，`KEY_ID` 使用空字符串槽位，调用身份由 `authorization` 解析出的 `authSubject` 或 token 指纹承担；历史项目已有 `x-app-key/appKey/keyId` 时只能作为兼容别名，它用于服务端查找密钥，不是密钥材料。
- `SIGN_ALG` 使用 `x-sign-alg` 或 envelope `sign-alg` 的原始字符串；参与签名的请求必须提供，且必须进入签名原文，防止算法标识被替换。
- `FUNC` 在握手阶段可以为空；业务消息必须填写 envelope 中的 `func`。
- `VERSION` 使用 `x-api-version` 或 envelope `version` 的原始字符串；TCP/UDP 不再额外传 `x-api-version`。
- `BODY_SHA256_HEX` 是原始 body bytes 或 canonical payload bytes 的 SHA-256 小写 hex。空 body 使用空字节数组的 SHA-256：`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`。

密钥标识规则：

- SDK/OpenAPI 和 WebSocket Upgrade Header 推荐统一使用 `x-api-key`；CMS HTTP/REST 不使用 `x-api-key`，使用登录主体、token 指纹和 `x-udid` 形成调用身份。
- TCP/UDP、WebSocket `AUTH` 和已认证 WebSocket 高风险业务消息 envelope 推荐统一使用 `api-key`。
- `x-api-key/api-key` 可以参与签名原文，防止攻击者替换密钥标识后复用签名；CMS HTTP/REST 的 `KEY_ID` 为空槽位时，签名原文仍必须保留该空行。
- 不允许把 HMAC secret、私钥或长期 token 当作 `x-api-key` 或 `api-key` 传输。
- 连接已完成认证且 session 唯一绑定密钥时，后续低风险消息可以省略消息级 `KEY_ID`；高风险消息必须携带 `api-key/KEY_ID`，不能只依赖连接级密钥上下文。

## 按入口构造 Canonical Request

实现时不要把所有入口条件写进一个巨大的 `SignatureVerifier`。推荐先由不同 builder 构造统一的 `CanonicalRequest`，再交给 `SignatureVerifier` 做算法校验。

| 构造器 | 场景 | 字段来源 | 特殊规则 |
| --- | --- | --- | --- |
| `HttpRequestCanonicalBuilder` | HTTP/REST CMS、SDK 或 OpenAPI 请求 | HTTP method、path、query、`x-reqid/x-timestamp/x-sign-alg/x-api-version`、可选 `x-api-key`、body bytes | CMS HTTP/REST 不使用 `x-api-key`，`KEY_ID` 为空槽位；CMS 登录后 replay key 使用 `authSubject + x-udid + x-reqid`；SDK/OpenAPI replay key 使用 `x-api-key + x-reqid`；公开登录、验证码、探活等无 token 接口 `UDID` 为空；必须支持 GET、POST `application/json`，CMS 还必须支持 POST `application/x-www-form-urlencoded`。 |
| `WebSocketUpgradeCanonicalBuilder` | WebSocket `signed-upgrade` | HTTP `GET`、Upgrade path、query、`x-reqid/x-timestamp/x-api-key/x-sign-alg/x-api-version`、空 body hash | `FUNC` 为空；`UDID` 为空，除非项目 API 标准另行定义可信 Header。 |
| `WebSocketAuthCanonicalBuilder` | WebSocket `auth-message` 首条 `AUTH` | 首条 AUTH envelope 的 `reqid/ts/api-key/sign-alg/version/func` 和原始消息体 bytes | `METHOD/PATH/CANONICAL_QUERY` 为空；`FUNC=AUTH`；短期票据只放 payload，不替代 `api-key`。 |
| `WebSocketMessageCanonicalBuilder` | 已认证 WebSocket 高风险业务消息 | envelope 的 `reqid/ts/api-key/sign-alg/version/func` 和原始 payload/frame bytes | `METHOD/PATH/CANONICAL_QUERY` 为空；`UDID` 使用空字符串槽位；不要要求 WebSocket 业务消息伪造 `udid`。 |
| `TcpAuthCanonicalBuilder` | TCP 首条 `AUTH` | TCP AUTH envelope 的 `reqid/ts/udid/api-key/sign-alg/version/func` 和原始 frame bytes | `METHOD/PATH/CANONICAL_QUERY` 为空；`FUNC=AUTH`；认证成功前禁止业务 func。 |
| `TcpUdpMessageCanonicalBuilder` | TCP/UDP 高风险业务消息 | envelope 的 `reqid/ts/udid/api-key/sign-alg/version/func` 和原始 payload/frame bytes | UDP 不使用 source address 填 `UDID`；`BODY_SHA256_HEX` 来源必须和客户端约定一致。 |

职责边界：

- `*CanonicalBuilder` 只提取字段、计算 body hash、组装 canonical string，不读取密钥、不比较签名。
- `SignatureVerifier` 只根据 `KEY_ID` 找密钥、校验 `sign-alg` 白名单并比较签名。
- `ReplayKeyResolver` 只从已解析安全字段构造 replay key。
- `ReplayCache` 只使用 `ReplayKeyResolver` 输出的 replay key 去重，可短 TTL 保存脱敏传输响应摘要；不重新拼 canonical string，也不构造 replay key，不保存业务幂等结果。
- 新增入口类型时新增 builder，不在既有 builder 中继续堆 `if/else`。

## HTTP/REST 请求体与 Query 规则

HTTP/REST CMS 和 SDK 签名必须先固定 query 与 body 的来源，再计算 `CANONICAL_QUERY` 和 `BODY_SHA256_HEX`，避免客户端按 JSON、服务端按表单或二次序列化后的对象计算签名。

| 请求类型 | `CANONICAL_QUERY` | `BODY_SHA256_HEX` |
| --- | --- | --- |
| GET | URL query 参数按名称升序和 RFC3986 编码后拼接 | 空字节数组 hash，不把 query 复制到 body |
| POST `application/json` | 只使用 URL query，不包含 JSON 字段 | 原始 request body bytes 的 SHA-256；不要解析后重新序列化 |
| CMS POST `application/x-www-form-urlencoded` | 只使用 URL query，不包含表单字段 | 原始 form body bytes 的 SHA-256；不要解析后重新排序、重新编码或重新拼接 |

规则：

- SDK 和 CMS 都必须支持 GET 与 POST `application/json` 的签名防篡改。
- CMS 还必须支持 `application/x-www-form-urlencoded` 表单提交的签名防篡改。
- 表单字段属于 body，不属于 query；除非字段确实出现在 URL 上，否则不要放入 `CANONICAL_QUERY`。
- 如果项目要求 canonical form body，必须单独定义表单字段排序、重复 key、空值和百分号编码规则，并要求客户端和服务端完全一致；没有明确规则时优先签原始 body bytes。
- `multipart/form-data`、文件上传和流式 body 不在默认规则内，需要单独定义摘要字段或上传前置签名策略。

## JSON Payload Hash

JSON payload 参与签名时优先使用原始接收 bytes 计算 hash，避免二次序列化造成字段顺序和空格差异。

如果业务必须对对象做 canonical JSON：

- key 按 Unicode 字典序升序。
- 字符串使用 JSON 标准转义。
- 数字不得改变精度或格式。
- 不输出无意义空格。
- `null`、空对象、空数组必须保留语义。

没有成熟 canonical JSON 实现时，不要自行手写复杂排序序列化；优先签原始 bytes。

## 算法建议

| 场景 | 建议 |
| --- | --- |
| CMS/SDK 与服务端共享密钥 | `HMAC-SHA256` |
| 第三方开放平台非对称密钥 | `RSA-SHA256` 或 `ECDSA-SHA256` |
| 内部服务调用 | 优先 mTLS，必要时叠加 `HMAC-SHA256` |

签名结果编码必须项目级固定，推荐 Base64；如果使用 hex，必须在接口标准中明确。

## 防重放规则

- 服务端校验 `x-timestamp` 或 envelope `ts` 与服务器时间偏差，默认窗口 `300s`。
- 服务端按入口类型写短 TTL 去重缓存，不同入口不得复用模糊 key。

| 入口 | Replay key 建议 | 说明 |
| --- | --- | --- |
| HTTP/REST CMS 登录后请求 | `http-cms:{authSubject}:{x-udid}:{x-reqid}` | CMS 不使用 `x-api-key`；`authSubject` 来自 `authorization` 解析结果或 token 指纹；`x-udid` 为空时受保护接口应先拒绝。 |
| HTTP/REST CMS 公开接口 | 不进入签名 replay cache | 登录、验证码、探活等公开接口默认不需要 token、签名或 `x-udid`；如项目要求公开接口也签名，使用 `http-cms-public:{path}:{clientIp}:{x-reqid}` 并叠加限流。 |
| HTTP/REST SDK 或 OpenAPI | `http-sdk:{x-api-key}:{x-reqid}:{authSubject|anonymous}` | SDK/OpenAPI 使用 `x-api-key` 定位调用方；登录后可追加 `authSubject`，公开接口使用 `anonymous` 并叠加限流。 |
| WebSocket `signed-upgrade` | `ws-upgrade:{x-api-key}:{x-reqid}:{authSubject|clientId}` | Upgrade 阶段能解析 token 时使用 `authSubject`，否则使用可验证的客户端标识。 |
| WebSocket `auth-message` 首条 `AUTH` | `ws-auth:{api-key}:{reqid}:{ticketId|authSubject|connectionId}` | 有短期票据时必须优先使用 `ticketId` 并保证单次使用；不要只依赖 `connectionId`。 |
| WebSocket 已认证高风险业务消息 | `ws-message:{api-key}:{reqid}:{authSubject|connectionId}` | 优先使用已认证主体；`connectionId` 仅在 `authSubject` 不可用时兜底；短 TTL 去重，重复 `reqid` 返回原响应摘要或拒绝。 |
| TCP `AUTH` 或高风险业务消息 | `tcp:{api-key}:{reqid}:{udid}` | `udid` 是设备或用户唯一标识，参与重放维度。 |
| UDP 高风险请求 | `udp:{api-key}:{reqid}:{udid}` | UDP source address 只能作为风控信号，不作为稳定身份。 |

- `x-sign` 或 `sign` 本身只证明内容未被篡改，不单独承担防重放；防重放依赖时间戳、请求唯一编号和 replay cache。
- 同一 `x-reqid` 或 `reqid` 在窗口内重复出现，应返回原响应摘要或拒绝为重放请求。
- replay cache 保存的是短 TTL 传输响应摘要或重放标记；订单、令牌、设备绑定等业务幂等结果必须进入 service 层的业务幂等存储。
- CMS 公开接口和匿名公开 UDP 探测没有稳定调用身份时不进入签名 replay cache；只能按 IP、path 或 `func`、时间窗口做限流和风控，不能把 source address 当成稳定身份。

## 示例

HTTP/WebSocket 握手：

```text
GET
/ws/token
client=web&env=prod
01HZREQID0001
1720000000000

app_cms_001
HMAC-SHA256

V1

e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

TCP/UDP 高风险业务消息：

```text



01HZREQID0002
1720000001000
device-001
app_sdk_001
HMAC-SHA256
TOKEN_UPLOAD
V2
5f70bf18a086007016f4b8a37a6d52e7798fe8c4e4bb1f3fca43d44e7f8f8b12
```

WebSocket 已认证高风险业务消息（`METHOD/PATH/CANONICAL_QUERY/UDID` 均为空槽位）：

```text



01HZREQID0003
1720000002000

app_ws_001
HMAC-SHA256
TOKEN_UPLOAD
V2
5f70bf18a086007016f4b8a37a6d52e7798fe8c4e4bb1f3fca43d44e7f8f8b12
```

## 验收清单

- 已固定字段顺序和换行方式。
- 已固定 query 排序和编码规则。
- 已固定 body hash 来源。
- 已说明空 body hash。
- 已说明 CMS HTTP/REST 不使用 `x-api-key`，SDK/OpenAPI 与 WebSocket Upgrade 使用 `x-api-key`，消息 envelope 使用 `api-key`。
- 已说明 `x-sign/sign`、`x-timestamp/ts`、`x-reqid/reqid` 的职责边界。
- 已说明 HTTP/REST GET、POST `application/json` 和 CMS POST `application/x-www-form-urlencoded` 的 query/body hash 来源。
- 已说明 TCP/UDP `udid` 是否进入签名原文和重放缓存维度。
- 已说明 CMS 公开接口和匿名公开 UDP 探测不进入签名 replay cache，只能限流或风控。
- 已说明 WebSocket 已认证高风险业务消息 replay key。
- 已说明哪些消息可以豁免消息级签名。
- 已按 HTTP、WebSocket Upgrade、WebSocket AUTH、WebSocket 高风险业务消息、TCP AUTH、TCP/UDP 高风险消息拆分 canonical builder。
