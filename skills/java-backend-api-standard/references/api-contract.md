# API 契约标准




## 目录

- [1. URL 与 HTTP 方法规则](#1-url-与-http-方法规则)
- [2. 通用请求头](#2-通用请求头)
- [3. 请求 Body 规则](#3-请求-body-规则)
- [4. 统一响应格式](#4-统一响应格式)
- [5. 分页格式](#5-分页格式)
- [6. 错误码约定](#6-错误码约定)
- [7. 参数校验与 i18n](#7-参数校验与-i18n)
- [8. OpenAPI 注解规则](#8-openapi-注解规则)
- [9. Netty 响应契约](#9-netty-响应契约)

## 1. URL 与 HTTP 方法规则

使用面向资源的 HTTP 路由。

推荐格式：

```text
/api/{version}/{module}/{resource}
/api/{version}/{module}/{resource}/{id}
```

示例：

```text
GET    /api/v1/system/users
POST   /api/v1/system/users
PUT    /api/v1/system/users/{id}
DELETE /api/v1/system/users/{id}
POST   /api/v1/orders/{orderNo}/cancel
```

方法规则：

- `GET`：只用于查询，不产生业务变更。
- `POST`：用于创建、提交、命令操作，或需要 body 的复杂查询。
- `PUT`：用于完整更新，或具有清晰替换语义的更新。
- `PATCH`：仅在项目明确支持部分更新时使用。
- `DELETE`：用于删除或逻辑删除。

避免 `/saveUser`、`/queryList`、`/doPay` 这类动作堆砌式路由。如果某个动作是领域命令，应显式建模，例如 `/orders/{orderNo}/cancel`、`/payments/{paymentNo}/confirm`。

## 2. 通用请求头

所有请求头统一使用小写命名。通用请求头：

```text
authorization: Bearer <token>，主要承载登录后的 token
accept-language: zh-CN / en-US
x-reqid: 前端或客户端为每次请求生成的唯一请求编号，服务端透传到响应 reqid
x-trace-id: 链路追踪 id，缺失时可由网关或后端生成
x-udid: 设备或用户唯一标识，用于登录后受保护接口的设备/用户上下文
x-timestamp: CMS 和 SDK 受保护接口的毫秒级请求时间戳，用于时间窗口校验
x-sign: CMS 和 SDK 受保护接口的防篡改签名结果
x-sign-alg: CMS 和 SDK 受保护接口的签名算法
x-api-version: CMS 和 SDK 受保护接口的契约版本
```

请求入参统一使用 `x-reqid` 请求头，不在 body 中定义公共 `reqid` 字段。`x-reqid` 由前端或客户端为每次请求生成，服务端校验后写入统一响应 JSON 的 `reqid` 字段，并用于访问日志、防重放和排查关联。
`x-udid` 是设备或用户唯一标识，但不是登录前天然存在的字段。登录、验证码、探活等公开接口不需要 token 或签名认证，也不具备 `x-udid`，必须通过 `auth-exclude-paths` 跳过整条认证链。未命中公开排除配置的受保护接口必须先校验 `x-udid`，为空直接返回统一错误，非空后再进入 token 或签名鉴权。

公开客户端、H5、移动端、开放平台、支付、回调 API 在通用请求头基础上额外要求：

```text
x-api-key: 客户端应用 key
```

除上表字段外，不再追加额外关联标识或幂等公共请求头。签名接口中，GET 使用规范化 query，POST JSON 使用 HTTP 原始 body 字节，CMS POST `application/x-www-form-urlencoded` 使用 HTTP 原始 form body bytes；body 为空时使用空字节。`authorization` 不承载签名结果，主要承载登录后的 token；签名结果统一放在 `x-sign`。SDK signed headers 顺序为 `x-timestamp;x-reqid;x-api-key;x-udid;x-sign-alg;x-api-version`，必须覆盖 `x-udid`，避免设备或用户唯一标识被篡改；SDK 防重放使用 `x-api-key + x-reqid`，CMS 登录后防重放使用 `authSubject + x-udid + x-reqid`；CMS 公开接口默认不进入签名 replay cache，必须叠加限流。幂等由业务请求字段、业务单号或业务唯一键承载。

管理后台 API 不使用 `x-api-key` 作为入参公参；后台受保护接口的登录态由 `authorization: Bearer <token>` 表达，设备或用户唯一标识由 `x-udid` 表达，防篡改签名由 `x-sign` 表达，签名算法由 `x-sign-alg` 表达，契约版本由 `x-api-version` 表达，权限授权在服务端完成。

## 3. 请求 Body 规则

请求 body 使用专用 request DTO。不要把 entity 暴露为 API 入参。

命名：

```text
CreateUserRequest
UpdateUserRequest
UserPageQuery
CancelOrderRequest
PaymentCallbackRequest
```

规则：

- Request DTO 只包含允许客户端提交的字段。
- `id`、`createdBy`、`createdTime`、`updatedBy`、`deleted`、内部状态等服务端管理字段，不得信任客户端输入。
- 时间字段使用 ISO-8601 字符串或文档化的 epoch milliseconds。每个项目选择一种并保持一致。
- 金额字段使用最小货币单位整数，例如分；或使用明确 scale 的 `BigDecimal`。绝不使用 `float` 或 `double`。
- 枚举字段使用稳定 code，不使用展示名称。
- JavaScript 无法安全表示的大数字 ID，在公开 API 中应使用字符串。

## 4. 统一响应格式

每个正常 HTTP API 返回统一包装：

```java
public class ApiResult<T> {
    private String reqid;
    private String code;
    private String message;
    private long ts;
    private T data;
}
```

推荐语义：

```json
{
  "reqid": "client-generated-request-id",
  "code": "000000",
  "message": "成功",
  "ts": 1716000000000,
  "data": {}
}
```

规则：

- `code = "000000"` 表示成功。
- 非 `000000` 的 `code` 表示业务错误或平台错误。
- `message` 是后端按错误码解析得到的展示或调试消息。
- `reqid` 来自客户端请求头 `x-reqid`，服务端写入响应 JSON，并用于访问日志关联；HTTP 请求缺失 `x-reqid` 时，错误响应使用空字符串保持 JSON 结构稳定，不得返回 `reqid: null`，也不得静默生成服务端 reqid。
- 客户端每次请求必须生成新的 `x-reqid`；受保护接口中 `x-reqid` 必须参与 `x-sign` 签名和防重放缓存。
- `ts` 是服务端生成响应时的 Unix epoch milliseconds。
- `traceId` 只保留在日志和内部链路追踪上下文中。不要放入公开 JSON 响应体。
- 不要混用响应形态，例如有时返回 `R`，有时返回 `Map`，有时直接返回 DTO。

## 5. 分页格式

使用一个共享分页响应对象：

```java
public class PageResult<T> {
    private List<T> list;
    private long total;
    private int page;
    private int pageSize;
    private long pages;
}
```

内存列表、样例服务或单元测试中的分页计算统一使用公共分页工具：

```java
PageSupport.ofList(all, page, pageSize)
```

数据库分页由 ORM、分页插件或 SQL 完成，但页码、页大小、总数和总页数语义必须与 `PageResult<T>` 保持一致。

查询参数命名：

```text
page=1
pageSize=20
sort=createdTime,desc
```

规则：

- 除非项目明确另有文档，页码从 `1` 开始。
- 最大页大小必须设置上限。
- 排序字段必须使用白名单。
- 除非数据库列名本身就是 API 契约的一部分，否则不要向公开客户端暴露原始数据库列名。

## 6. 错误码约定

使用中心化错误码枚举或注册表。

推荐格式：

```text
000000   success
SMEEEE   failure code
```

推荐接口：

```java
public interface ErrorCode {
    String code();
    String messageKey();
    String defaultMessage();
}
```

规则：

- `ErrorCode` 和 `CommonErrorCode` 属于公共 API 结果码契约，推荐包名为 `common.code`；异常类、全局异常处理器和字段错误对象放 `common.exception`，不要用 `common.error` 混放错误码与异常处理。
- 失败码使用 6 位字符串格式 `SMEEEE`。
- `S` 是 1 位大写系统码，`M` 是 1 位大写模块码，`EEEE` 是 4 位错误编号。
- 保留 `9999` 作为系统或模块兜底错误，例如 `AC9999`。
- 公共码示例：`AC0001` 参数错误，`AC0002` 未认证，`AC0009` 签名无效。
- 业务码示例：`AU0001` 用户不存在，`AP0001` 支付单不存在。
- `ErrorCode` 和 `CommonErrorCode` 不得携带 `httpStatus`。已进入应用并被统一处理的认证失败、签名失败、防重放失败、参数校验失败、业务冲突等结果，HTTP 层统一返回 200，通过响应体 `code/message/data` 表达业务结果。
- 未命中路由、HTTP method 不支持、网关不可用、服务不可达、未被全局处理器捕获的系统异常等传输层或平台故障，可以继续使用对应 HTTP 状态，例如 404、405、502、503、500。
- 正常业务失败必须携带稳定错误码，但不得把“用户不存在、余额不足、状态不允许、参数不合法、未登录、无权限、幂等冲突”等可预期分支当作程序异常抛出并打印 `error` 堆栈；优先使用 `Result`、`Decision`、`Optional`、领域错误对象或统一响应转换表达。
- 如果历史项目保留 `BusinessException`，它只能作为 Controller/Adapter 边界到统一响应的兼容机制，不得成为 service/domain 常规控制流；不得对这类可预期业务失败打印 `log.error`。
- 参数校验失败必须转换为同一个 `ApiResult` 格式；框架抛出的校验异常由全局处理器转换响应，但不作为系统异常统计。
- 任何 `catch` 块不得空处理、只写注释或只返回默认值。若当前层消费程序异常、依赖异常、审计保存异常、协议解析器缺陷、ACK/响应写出失败或其他不可预期异常，必须使用 `log.error` 记录脱敏后的异常日志；只允许纯包装后继续 `throw` 的异常交给上层全局异常处理器统一记录。客户端协议格式错误、字段格式错误和参数校验失败属于可预期拒绝，返回稳定错误码并进入访问日志/metrics，不打印 `log.error` 堆栈。
- 不要向客户端暴露堆栈、SQL 错误、类名或内部异常消息。
- 一旦被前端或第三方消费，错误码必须保持稳定。

## 7. 参数校验与 i18n

在 request DTO 上使用 Bean Validation 注解：

```java
@NotBlank(message = "{user.username.required}")
@Size(max = 32, message = "{user.username.size}")
private String username;
```

规则：

- 校验消息使用 i18n key，不要在 DTO 注解里硬编码中文。
- 默认中文消息配置在 `ValidationMessages_zh_CN.properties` 或项目消息资源中。
- 即使中文文案变化，也要保持 message key 稳定。
- 全局异常处理器负责把参数校验失败转换为统一响应。

## 8. OpenAPI 注解规则

需要生成 API 文档的项目，应在 controller 和 DTO 上添加注解：

```java
@Tag(name = "User Management")
@Operation(summary = "Create user")
@Schema(description = "Username")
```

规则：

- OpenAPI 注解描述契约，但不能替代参数校验。
- 请求和响应示例必须匹配真实统一响应包装。
- OpenAPI 示例必须展示 `ApiResult<T>` 外壳，不得只展示裸 DTO。
- 生产环境必须关闭 Swagger UI/OpenAPI UI，或通过网关、登录态、IP 白名单等方式保护。
- 废弃字段必须标记迁移说明。

## 9. Netty 响应契约

TCP、UDP 和 Netty WebSocket 不使用 HTTP 状态码表达业务结果，但必须复用统一响应模型：

```json
{
  "reqid": "same-as-request",
  "code": "000000",
  "message": "成功",
  "ts": 1716000000000,
  "data": {}
}
```

规则：

- 响应和 ACK 顶层只包含 `reqid/code/message/ts/data`。
- 响应体不返回 `func/version/traceId/status`。
- ACK 的确认对象和状态放入 `data.ackFunc`、`data.ackStatus`、`data.receivedSeqno`。
- 失败码仍使用 `SMEEEE` 格式，含义与 HTTP API 保持一致。
- Netty envelope、心跳和 handler 分发规则见 `netty-transport-standard.md`。

统一响应示例：

```json
{
  "reqid": "client-generated-request-id",
  "code": "000000",
  "message": "成功",
  "ts": 1716000000000,
  "data": {
    "id": "900001",
    "name": "demo"
  }
}
```
