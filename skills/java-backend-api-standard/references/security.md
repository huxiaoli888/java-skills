# 安全、防重放、防篡改与可靠性




## 目录

- [1. 安全档位](#1-安全档位)
- [2. 防重放参数](#2-防重放参数)
- [3. 防篡改签名](#3-防篡改签名)
- [4. 签名 Payload 规范](#4-签名-payload-规范)
- [5. 幂等](#5-幂等)
- [6. 日志与审计](#6-日志与审计)
- [7. CORS 跨域](#7-cors-跨域)
- [8. SQL 注入防护](#8-sql-注入防护)
- [9. 限流](#9-限流)
- [10. 文件上传安全](#10-文件上传安全)
- [11. Netty TCP/UDP/WebSocket 安全](#11-netty-tcpudpwebsocket-安全)

## 1. 安全档位

### 内部后台 API

最低要求：

- 登录 token 或 session 认证。
- 受保护接口请求头携带 `x-udid`，表示设备或用户唯一标识。
- 受保护接口请求头携带 `x-sign`，表示基于当前请求计算出的防篡改签名结果。
- 登录、验证码、探活等公开接口不需要 token 或签名认证，也不具备 `x-udid`，必须通过 `auth-exclude-paths` 配置排除整条认证链。
- 未命中公开排除配置的接口必须先校验 `x-udid`，为空直接返回统一错误，非空后再进入 token 鉴权和 `x-sign` 验签。
- 管理后台 API 不使用 `x-api-key` 作为入参公参。
- 基于角色或权限码的授权。
- 服务端输入校验。
- 全局异常处理。
- 对新增、修改、删除、导入、导出、权限和配置变更记录操作审计日志。
- 对登录、导出等敏感接口限流。

如果使用 cookie 认证，需要评估 CSRF 防护。如果使用 bearer token，需要通过 HTTPS 和合理过期时间保护 token。
后台 API 使用 `authorization: Bearer <token>` 表达登录态，使用 `x-udid` 表达设备或用户唯一标识，使用 `x-sign` 表达请求防篡改签名，权限授权仍然必须在服务端完成。
`udid-exclude-paths` 只表示跳过 `x-udid` 前置校验，不代表跳过 token 或 `x-sign` 验签。登录、验证码、探活等公开入口如果不需要 token 或签名认证，必须放入 `auth-exclude-paths`。不要用 `udid-exclude-paths` 伪装认证白名单。

### 移动端或 H5 API

最低要求：

- HTTPS。
- Token 认证。
- 敏感 API 使用 `x-timestamp` 校验时间窗口，使用按调用方类型拆分的 replay key 防重放，不再使用 `x-nonce`。
- 当客户端在威胁模型下能够相对安全地持有 app secret 时，使用 `x-sign` 承载签名结果，并按 GET query、POST JSON raw body 或 CMS form body 规范生成签名 payload。
- 按用户、设备、IP 和 app 维度在适当位置限流。
- 业务风控需要时传递设备或客户端版本请求头。

### 开放平台 API

最低要求：

- `x-api-key`。
- 每个客户端独立 secret 或非对称密钥。
- `x-sign`、`x-timestamp`、`x-reqid`，并按标准签名 payload 规则完成防篡改校验；需要登录态时，`authorization` 只承载 token。
- 重放缓存。
- 合作方集成需要更强信任时，使用 IP 白名单或 mTLS。
- 契约版本管理。
- 配额和限流。
- 外部调用方可集成的专用错误码。

### 订单、支付、回调或高风险交易 API

最低要求：

- 调用方是外部系统时，满足所有开放平台安全要求。
- 可重试写操作使用业务唯一键。
- 唯一业务键和数据库约束。
- 不可逆状态变更使用状态机。
- 不可变审计记录。
- 支付和回调流程具备对账记录。
- 金额不使用 `float` 或 `double`。
- 任何状态变更前先验证回调签名。

## 2. 防重放参数

防重放请求至少需要：

```text
x-timestamp
x-reqid
x-sign
```

推荐补充：

```text
x-sign-alg
x-api-version
```

校验规则：

- 请求头名称统一小写。
- 拒绝超出允许窗口的时间戳，常见窗口为 5 分钟。
- 按调用方类型在 Redis 或其他高速存储中保存短 TTL replay key，不能所有入口共用模糊 key。
- SDK/OpenAPI replay key 使用 `x-api-key + x-reqid`。
- CMS 登录后 replay key 使用 `authSubject + x-udid + x-reqid`，其中 `authSubject` 来自 `authorization` 解析后的登录主体或 token 指纹。
- CMS 登录、验证码、探活等公开接口不需要 token、签名或 `x-udid`，不进入签名 replay cache；如项目要求公开接口也带签名，则 replay key 使用 `anonymous + path + clientIp + x-reqid` 并叠加限流。
- 在重放窗口内拒绝重复 `x-reqid`。
- 签名输入包含 method、path、规范化 query、timestamp、reqid、调用方身份、签名算法、API 版本和规范化 payload 字节。
- 可行时使用恒定时间比较签名。

## 3. 防篡改签名

推荐 canonical bytes：

```text
UTF8(
  METHOD + "\n" +
  PATH + "\n" +
  CANONICAL_QUERY + "\n" +
  TIMESTAMP + "\n" +
  REQID + "\n" +
  CALLER_KEY + "\n" +
  SIGNATURE_ALG + "\n" +
  API_VERSION + "\n"
) + RAW_BODY_BYTES
```

示例：

```text
POST
/api/v1/orders
channel=h5&scene=buy
1716000000000
req-20260727-000001
user-123|device-456
HMAC-SHA256
v1
{"orderNo":"A1001","amount":100}
```

然后使用项目批准的算法签名，通常是 HMAC-SHA256：

```text
base64(hmacSha256(secret, canonicalBytes))
```

规则：

- 查询参数按 key 排序；如果允许重复 key，再按 value 排序。
- 百分号编码必须一致。
- 签名结果不参与自身签名；签名结果放在 `x-sign` 中。
- GET 请求 body 为空，query 必须按 key 排序；如果允许重复 key，再按 value 排序。
- POST JSON 必须把 HTTP 原始 body 字节加入签名输入；body 为空时使用空字节。
- CMS POST `application/x-www-form-urlencoded` 表单提交必须把 HTTP 原始 form body bytes 加入签名输入，不解析后重新排序、重新编码或重新拼接。
- SDK 不要求支持 `application/x-www-form-urlencoded` 表单签名，默认支持 GET 和 POST JSON。
- 大文件上传不建议直接把完整文件字节纳入普通 API 签名，应使用对象存储预签名上传、分片上传协议或项目批准的文件签名方案。

推荐签名请求头：

```text
x-sign: <base64-signature>
```

规则：

- `authorization` 不承载签名结果，主要承载登录后的 token。
- `x-sign` 只承载签名结果，不承载 credential、algorithm 或 signed headers。
- `x-api-key` 表达 SDK/API 调用方；CMS 不使用 `x-api-key` 作为后台公参。
- `x-sign-alg` 表达签名算法，必须与服务端允许算法一致。
- 参与签名的请求头按项目标准保持小写和稳定顺序，首版 SDK 建议为 `x-timestamp;x-reqid;x-api-key;x-udid;x-sign-alg;x-api-version`；CMS 建议为 `x-timestamp;x-reqid;authorization;x-udid;x-sign-alg;x-api-version`。SDK 与 CMS 都必须把 `x-udid` 纳入签名 canonical，避免设备或用户唯一标识被篡改后仍通过验签。

## 4. 签名 Payload 规范

问题：H5、移动端或后端如果各自重新序列化 JSON，字段顺序、空白、null 处理、日期格式、数字格式都可能不同，导致签名不一致。

标准方案：

1. 签名 HTTP 原始请求体字节。
   - 客户端对实际发送到网络上的 body 字节签名。
   - 后端在 JSON 解析前读取并缓存原始 body。
   - 后端验签使用缓存的原始 body 字节，而不是反序列化后的 Java 对象。

2. 明确空 body 和编码规则。
   - body 缺失时使用空字节参与签名。
   - JSON 请求使用 `application/json; charset=UTF-8`。
   - 如果启用压缩或网关改写 body，必须明确签名的是网关改写前还是改写后的字节，并保证客户端、网关和后端一致。

3. 表单请求按模块区分。
   - CMS 支持 `application/x-www-form-urlencoded` 表单提交，签名输入为 HTTP 原始 form body bytes。
   - SDK 不要求支持 form-urlencoded 签名，默认只支持 GET 和 POST JSON。
   - 客户端和服务端必须使用同一份跨语言测试样例验证空值、重复 key、百分号编码和 body 原文字节一致性。

除非严格定义了规范化规则，否则不要在反序列化后对 Java 对象签名。

## 5. 幂等

可重试写操作使用业务报文中的唯一业务键，不定义公共 `idempotencyKey` 入参或请求头：

```text
clientToken / requestNo / businessNo / orderNo: 调用方为本次意图操作生成或携带的唯一业务键
```

服务端存储应记录：

```text
userId or apiKey
requestSignatureInputFingerprint
businessType
businessKey
status
responseSnapshot or result reference
createdTime
expireTime
```

规则：

- 业务层从请求 DTO 中抽取 `businessKey`，例如 `orderNo`、`paymentNo`、`requestNo` 或 `businessNo`。
- 相同 `businessType + businessKey` 加相同请求，在安全时返回原始结果。
- 相同 `businessType + businessKey` 加不同请求，返回幂等冲突错误。
- 支付/订单创建还必须在数据库中强制唯一业务约束。
- 幂等不能替代事务隔离或状态校验。

## 6. 日志与审计

访问日志应记录：

```text
traceId, reqid, userId/apiKey, method, path, statusCode, code, message, requestTime, responseTime, duration, clientIp, requestBody
```

`code` 和 `message` 必须来自统一响应 `ApiResult` 或安全拦截器写出的统一错误响应，不通过记录完整 response body 获取。
全局访问日志应记录接口接收到报文的请求时间和返回报文的时间。请求体在进入 controller 前读取并缓存，避免后续业务代码无法再次读取 body。
访问日志中的 `udid` 和 `apiKey` 默认作为调用身份原值记录；`requestBody` 必须经过请求体脱敏策略处理后再写日志，默认脱敏 password、token、secret、captcha、smsCode、idCard、bankCard 等敏感字段。

操作审计日志应记录：

```text
operator, operationType, businessId, before/after summary, result, traceId, timestamp
```

规则：

- 不记录 `authorization`、`x-sign`、secret、私钥或原始 token。
- 按项目策略脱敏手机号、邮箱和标识符。
- 后台新增、修改、删除、导入、导出、权限和配置变更接口应使用操作审计注解或等价 AOP 机制。
- 敏感操作审计日志应持久化且可查询。
- 普通操作日志可以异步记录；关键交易审计不能静默丢失。
- 禁止吞异常。任何 `catch` 块不得空处理、只写注释、只返回默认值或只用 `warn` 记录后继续隐藏问题。当前层如果消费程序异常、依赖异常、审计保存异常、协议解析器缺陷、ACK/响应写出失败或其他不可预期异常，必须使用 `log.error` 记录脱敏日志，至少包含 `reqid/traceId`、接口或阶段、错误码和异常类型；只有继续 `throw` 给全局异常处理器的场景可以不在当前层重复打印。
- 正常业务失败不属于程序异常，例如未登录、无权限、参数错误、客户端协议格式错误、签名失败、重放请求、资源不存在、状态不允许、幂等冲突。它们必须返回稳定错误码并计入业务/安全指标，不得为了排查方便主动抛异常并打印 `log.error` 堆栈。

## 7. CORS 跨域

CORS 是浏览器安全策略配置，不等同于后端认证、签名、防重放或权限控制。所有前后端分离项目必须显式配置跨域策略，不得依赖框架默认行为或在 controller 上零散使用 `@CrossOrigin`。

最低要求：

- 使用统一 `ApiCorsConfiguration` 和 `ApiCorsProperties` 配置跨域。
- 允许来源、方法、请求头、暴露响应头、凭证模式和缓存时间必须配置化。
- 开发环境可以允许本地前端地址，例如 `http://localhost:5173`。
- 生产环境必须配置明确域名，不允许在 `allow-credentials: true` 时使用 `*`。
- 不要把 `authorization`、`x-sign`、`x-api-key`、`x-reqid`、`x-timestamp` 等安全头从签名或鉴权规则中移除；CORS 只决定浏览器是否允许发送这些头。
- CMS 与 SDK 模块可以共用 CORS 基础设施，但生产环境应按模块暴露域名分别配置。

推荐配置项：

```yaml
app:
  web:
    cors:
      enabled: true
      path-pattern: /**
      allowed-origins:
        - http://localhost:5173
      allowed-origin-patterns: []
      allowed-methods:
        - GET
        - POST
        - PUT
        - DELETE
        - OPTIONS
      allowed-headers:
        - authorization
        - accept-language
        - content-type
        - x-api-key
        - x-timestamp
        - x-reqid
        - x-sign
        - x-sign-alg
        - x-api-version
        - x-trace-id
        - x-udid
      exposed-headers:
        - x-trace-id
      allow-credentials: true
      max-age: 1800
```

## 8. SQL 注入防护

SQL 注入不能只靠一个 HTTP Filter 解决。标准防护应分层完成：入口轻量拦截明显攻击特征，业务层限制字段语义，Mapper/SQL 层使用参数绑定和白名单。

最低要求：

- Mapper 层禁止使用 `${}` 拼接前端传入值，优先使用 `#{}` 参数绑定。
- 复杂 SQL 参考 renren 项目做法放到 Mapper XML 中，Java 代码不拼接长 SQL，不用注解承载复杂动态 SQL。
- 排序字段、查询字段、分组字段、表名、列名等不能直接使用前端原值，必须使用服务端白名单映射。
- 动态排序方向只能接受 `asc` 或 `desc`，并规范化为固定枚举。
- 分页大小、导出数量和模糊查询长度必须有限制。
- 全局异常不得向客户端暴露 SQL 原始错误、表名、字段名、数据库类型或堆栈。
- 可选启用 `SqlInjectionFilter` 对 query string 和表单参数做明显攻击特征拦截；JSON body 不在该 filter 中重新解析，避免破坏 raw body 签名和请求体缓存。
- `SqlInjectionGuard` 只能作为第一道信号，不能替代 Mapper 白名单、参数绑定、权限控制和代码审查。

推荐配置项：

```yaml
app:
  security:
    sql-injection:
      enabled: true
      check-query-parameters: true
      check-form-parameters: false
      exclude-paths:
        - /actuator/health
```

## 9. 限流

公司级生产标准必须具备限流入口，生成器示例可提供服务端兜底限流能力。生产环境优先使用网关限流、WAF 或服务网格限流，应用内限流作为第二道保护。

最低要求：

- 登录、验证码、导出、短信、支付、下单、回调等敏感接口必须定义限流规则。
- 限流维度至少支持 path、method、调用身份和 IP；调用身份优先使用 `x-api-key`、`x-udid` 或登录用户。
- 开发示例可以使用本地内存限流；多实例生产环境必须替换为 Redis、网关或其他分布式限流。
- 限流命中返回统一响应，错误码使用 `AC0006`。
- 限流规则必须配置化，不能散落在 controller 或业务代码中。

推荐配置项：

```yaml
app:
  security:
    rate-limit:
      enabled: true
      default-permits: 120
      default-window: 1m
      identity-headers:
        - x-api-key
        - x-udid
      exclude-paths:
        - /actuator/health
      rules:
        - path-pattern: /auth/login
          permits: 20
          window: 1m
```

## 10. 文件上传安全

文件上传接口必须单独设计，不要把普通 JSON API 签名方案直接套到大文件字节上。

最低要求：

- 限制上传大小、扩展名和 content type。
- 文件名不得直接作为服务端存储路径，必须重新生成对象 key。
- 不信任客户端 content type，生产环境应结合魔数、杀毒、内容扫描或对象存储策略。
- 大文件优先使用对象存储预签名上传、分片上传或网关上传，业务 API 只接收文件引用。
- 上传结果中的访问 URL 必须按权限控制，不要默认返回永久公开地址。

推荐配置项：

```yaml
app:
  security:
    file-upload:
      enabled: true
      max-bytes: 10485760
      allowed-extensions:
        - jpg
        - jpeg
        - png
        - pdf
        - xlsx
      allowed-content-types:
        - image/jpeg
        - image/png
        - application/pdf
```

## 11. Netty TCP/UDP/WebSocket 安全

Netty 入口需要认证、防篡改、防重放、限流和审计时，HTTP API 的请求头、签名和统一响应契约仍以本 skill 的对应 reference 为准。

TCP、UDP、WebSocket 的 envelope、消息级安全字段、replay key、ACK、handler dispatcher、连接治理和协议异常处理，详细规则由 `netty-handler-dispatcher` 维护；本文件只保留当前场景下的摘要和路由。
