# 实现标准




## 目录

- [1. 基线选择](#1-基线选择)
- [2. HTTP 状态与业务结果策略](#2-http-状态与业务结果策略)
- [3. 统一响应细节](#3-统一响应细节)
- [4. 错误码格式](#4-错误码格式)
- [4.1 业务失败与异常边界](#41-业务失败与异常边界)
- [5. 参数校验错误结构](#5-参数校验错误结构)
- [6. JSON 与时间约定](#6-json-与时间约定)
- [7. Spring Boot 代际差异](#7-spring-boot-代际差异)
- [8. 持久化栈选择](#8-持久化栈选择)
- [9. 安全过滤器决策](#9-安全过滤器决策)
- [10. 环境配置](#10-环境配置)
- [11. 规则应用与生成器边界](#11-规则应用与生成器边界)
- [12. 公司级生产基线](#12-公司级生产基线)

## 1. 基线选择

生成项目前，先询问或推断这些选择：

```text
JDK: 8 / 11 / 17 / 21
Spring Boot: 2.x / 3.x / 4.x
Build: Maven
Persistence: MyBatis-Plus / MyBatis / JPA
Authentication: Spring Security / Sa-Token / Shiro / existing framework
API docs: springdoc-openapi / Swagger2 / none
Project shape: single module / multi-module
Security profile: admin / mobile-H5 / open-platform / transaction
```

当用户未指定时，新项目推荐默认值：

```text
JDK 17
Spring Boot 4.0.5 for the current scaffold, or company-approved 3.3.x when Spring Cloud/Nacos compatibility requires it
Maven
需要认证时使用 Spring Security
需要 API 文档时使用 springdoc-openapi
除非存在真实模块边界，否则先使用单模块
```

如果现有代码库是 Spring Boot 2.x 或 JDK 8，应遵循现有技术栈，而不是强行升级默认值。

## 2. HTTP 状态与业务结果策略

默认使用以下策略：

```text
HTTP 200: 请求到达应用并被统一处理，业务结果由响应体 code/message/data 表达
HTTP 404/405: 路由不存在或 HTTP method 不支持
HTTP 413/415: 网关或容器层拒绝的请求体过大、媒体类型不支持
HTTP 429/502/503/504: 网关、限流网关或上游平台层故障
HTTP 500: 未被全局处理器捕获的非预期系统异常
```

生成项目中，认证失败、无权限、签名失败、防重放失败、参数校验失败、幂等冲突、业务状态不允许、资源不存在等已进入应用并被统一处理的结果，均返回 HTTP 200，并通过响应体 `code` 区分失败原因。

`ErrorCode` 与 `CommonErrorCode` 不得携带 `httpStatus` 字段或方法，避免把传输层状态和业务错误码绑定。访问日志可以记录实际 HTTP 响应状态，但它只是传输结果；已处理业务失败通常记录为 200。

不要在响应体中返回堆栈或原始异常消息。

## 3. 统一响应细节

使用此响应结构：

```json
{
  "reqid": "client-generated-request-id",
  "code": "000000",
  "message": "成功",
  "ts": 1716000000000,
  "data": {}
}
```

固定决策：

```text
code 类型: String
成功码: 000000
success 字段: 默认省略，因为 code 已表达成功/失败
reqid: 公开 JSON 响应中必须存在，来自客户端请求头 x-reqid
ts: 公开 JSON 响应中必须存在，表示服务端响应时间，epoch milliseconds
traceId: 只用于日志和内部链路追踪；不要放入公开 JSON 响应体
空成功 data: 命令 API 使用 null，空列表使用 []，分页使用 list 为空的 PageResult
message: 后端解析出的本地化展示/调试消息
data: 强类型 DTO，绝不直接返回 entity
```

参数校验失败时，`data` 可以包含字段级错误详情。普通业务失败时，除非 API 契约明确规定结构化错误数据，否则 `data` 保持 `null`。

## 4. 错误码格式

默认字符串错误码：

```text
000000 成功
AC0001 参数或校验错误
AC0002 认证错误
AC0003 鉴权错误
AC0004 资源不存在
AC0005 冲突、重复提交或幂等冲突
AC0006 请求被限流
AC0007 请求已过期
AC0008 重放请求
AC0009 签名无效或请求被篡改
AC9999 系统内部兜底错误
```

业务模块使用 `SMEEEE`：

```text
S      系统码，1 位大写字母
M      模块码，1 位大写字母
EEEE   模块内 4 位错误编号
```

示例：`AU0001` 表示 A 系统用户模块的用户不存在；`AP0001` 表示 A 系统支付模块的支付单不存在。

命名规则：

```text
SUCCESS
PARAM_INVALID
UNAUTHORIZED
FORBIDDEN
RESOURCE_NOT_FOUND
SIGNATURE_INVALID
REPLAY_REQUEST
IDEMPOTENCY_CONFLICT
SYSTEM_ERROR
USER_NOT_FOUND
ORDER_STATUS_INVALID
```

规则：

- 每个 code 对应一个枚举常量、一个 message key 和一个默认消息。
- 不要把已废弃错误码复用于不同含义。
- 新增业务错误码放在所属模块范围内。
- 外部/开放平台错误码属于公开契约，需要保持向后兼容。

## 4.1 业务失败与异常边界

正常业务失败是可预期分支，不是程序异常。实现时必须区分：

- 可预期业务失败：参数校验失败、资源不存在、状态不允许、余额不足、库存不足、重复提交、未登录、无权限、签名失败、重放请求等，返回稳定错误码和统一响应；不得用 `log.error` 打印异常堆栈污染健壮性判断。
- 程序异常：空指针、编码错误、序列化失败、数据库/Redis/MQ/HTTP 依赖异常、审计持久化失败、未知运行时异常等，必须被全局异常处理器或当前消费层用 `log.error` 记录脱敏日志。
- service/domain 层不要把正常业务分支写成异常控制流；优先返回 `Result`、`Decision`、领域错误对象或 `Optional`，由 application/controller 边界转换成统一响应。
- 历史项目如保留 `BusinessException`，仅作为边界兼容和统一响应转换手段；新增核心业务规则不得依赖抛业务异常推进正常流程。

## 5. 参数校验错误结构

推荐字段错误模型：

```java
public class FieldErrorItem {
    private String field;
    private String message;
    private String messageKey;
    private Object rejectedValue;
}
```

推荐校验失败响应：

```json
{
  "reqid": "client-generated-request-id",
  "code": "AC0001",
  "message": "请求参数不合法",
  "ts": 1716000000000,
  "data": [
    {
      "field": "username",
      "message": "用户名不能为空",
      "messageKey": "user.username.required"
    }
  ]
}
```

规则：

- 对敏感 rejected value 做脱敏。
- DTO 注解中使用 `{message.key}`。
- 在全局异常处理器中解析面向用户的消息。

## 6. JSON 与时间约定

默认约定：

```text
JSON 命名: lowerCamelCase
请求 Content-Type: application/json; charset=UTF-8
响应 Content-Type: application/json; charset=UTF-8
公开 API 日期时间: 带时区的 ISO-8601 字符串，除非项目标准要求 epoch milliseconds
响应公共字段: reqid, ts；reqid 来自客户端请求头 x-reqid
JavaScript 不安全大整数 ID: String
金额: 最小货币单位整数，或明确 scale 的 BigDecimal
```

除非对接第三方契约要求，否则不要混用 snake_case 和 camelCase。

## 7. Spring Boot 代际差异

Spring Boot 2.x：

```text
Bean Validation imports: javax.validation.*
Servlet imports: javax.servlet.*
Swagger option: Springfox Swagger2 或兼容 Boot 2 的 springdoc 版本
```

Spring Boot 3.x 和 4.x：

```text
Bean Validation imports: jakarta.validation.*
Servlet imports: jakarta.servlet.*
OpenAPI option for Boot 3.x: springdoc-openapi 2.x
OpenAPI option for Boot 4.x: springdoc-openapi 3.x
MyBatis-Plus starter for Boot 4.x: mybatis-plus-spring-boot4-starter
```

实现或生成代码时，按所选代际更新导入。

## 8. 持久化栈选择

MyBatis-Plus：

- 适合 CRUD 后台系统。
- Wrapper 保持在 repository/mapper/service 内部，不要放到 controller。
- 避免 controller 直接返回 entity。

MyBatis：

- 适合 SQL 必须显式控制的场景。
- 复杂 SQL 参考 renren 项目做法，通过 `src/main/resources/mapper/**/*.xml` 实现；Java Mapper 接口只保留方法签名和参数声明。
- 多表关联、动态条件、报表统计、导出查询、数据权限拼装、数据库方言差异和较长 SQL 不写在注解或 service 字符串中。
- 投影复杂时，保持 SQL 结果对象与 API response DTO 分离。

JPA：

- 适合需要聚合映射和 repository 抽象的场景。
- 避免在 controller 中触发懒加载问题。
- 在 service/converter 边界把 entity 转成 response DTO。

## 9. 安全过滤器决策

签名 API 推荐请求链路：

```text
trace id filter
request body cache filter
auth-exclude-paths check
udid precheck filter
authentication filter
signature verification filter
replay protection filter
idempotency filter for write APIs
controller
```

规则：

- 签名失败返回 `SIGNATURE_INVALID`。
- 签名验签必须统一使用规范化 payload：GET query 排序，POST JSON 使用 raw body，CMS form-urlencoded 使用原始 form body bytes，不解析后重新排序、重新编码或重新拼接。
- `auth-exclude-paths` 只用于登录、验证码、探活等公开接口；这些接口不需要 token 或签名认证，也不具备 `x-udid`。
- `udid-exclude-paths` 只跳过 `x-udid` 前置校验；不能跳过 token 或 `x-sign` 验签。
- 时间戳过期返回 `REQUEST_EXPIRED`。
- `x-reqid` 重复返回 `REPLAY_REQUEST`。
- 相同 `businessType + businessKey` 搭配不同 `requestFingerprint` 返回 `IDEMPOTENCY_CONFLICT`。
- 支付/开放平台 API 在 Redis/cache 不可用时应失败关闭；只有明确低风险的内部 API 才可在文档化后失败开放。

## 10. 环境配置

前后端分离项目必须显式拆分环境配置，避免开发默认值进入测试或生产环境。

推荐资源结构：

```text
src/main/resources/
|-- application.yml
|-- application-dev.yml
|-- application-test.yml
`-- application-prod.yml
```

职责划分：

| 文件 | 职责 |
| --- | --- |
| `application.yml` | 通用配置、应用名、端口、context-path、默认激活环境、公共配置结构 |
| `application-dev.yml` | 本地开发配置，可使用本地前端域名、开发 token、测试 apiKey/secret |
| `application-test.yml` | 测试环境配置，使用测试域名和测试密钥占位，不允许使用开发端口或开发密钥 |
| `application-prod.yml` | 生产环境配置，敏感值必须来自环境变量、配置中心或密钥系统，禁止默认密钥 |

规则：

- 默认 `spring.profiles.active` 可以是 `dev`，但生产部署必须由启动参数、环境变量或配置中心覆盖。
- 生产环境不得保留 `change-me`、`dev-token`、`test-api-key`、`test-secret` 等开发占位值。
- 生产 CORS 必须配置明确域名；`allow-credentials: true` 时禁止 `*` 或无约束 `allowed-origin-patterns`。
- CMS 与 SDK 模块可以各自维护配置文件，但配置项命名、层级和含义必须一致。
- 本地开发和测试可以使用内存 replay request store、内存幂等、日志型审计；生产环境必须按 `production-replacement.md` 替换。
- 配置说明必须写入项目文档，至少覆盖服务端口、context-path、安全、CORS、SQL 注入、防重放、幂等和生产替换项。

## 11. 规则应用与生成器边界

本技能只提供标准规则和检查器，不再携带 Java 基础代码资产。

应用规则时：

- 先判断现有项目是否已有等价基础设施，避免重复引入第二套响应、异常、认证或日志体系。
- 需要从零生成 common/cms-api/sdk-api 多模块项目、基础设施代码或 CRUD 样例时，使用 `java-backend-project-generator`。
- 普通 CRUD 设计必须参考 `references/crud-standard.md`；分页计算、审计字段填充、雪花 ID、逻辑删除常量必须与项目公共基础设施保持一致。
- 使用操作审计 AOP 时，项目必须引入 AOP/AspectJ 支持。Spring Boot 2.x/3.x 项目如果 BOM 已管理 `spring-boot-starter-aop`，可直接使用该 starter；Spring Boot 4.x 项目应先用 Maven 验证依赖管理，若 starter 未被 BOM 管理，则使用 `spring-aop` + `aspectjweaver`。不要在未验证版本管理的情况下把 `spring-boot-starter-aop` 硬编码进项目。
- 生产环境应将内存版 replay/credential/audit 示例替换为 Redis、数据库或项目批准的持久化实现。
- 如果项目已有等价类，匹配现有代码风格。

## 12. 公司级生产基线

新建公司级 Java 后端项目，除 API 契约和分层结构外，默认还应具备以下生产基线：

```text
统一配置分层
统一生产技术栈和版本兼容策略
统一错误码与响应报文
统一认证、签名、防重放、防篡改
统一访问日志与操作审计
统一数据库迁移、审计表、幂等表和唯一约束
统一 CMS 权限、数据权限和多租户边界
统一 CORS、SQL 注入边界防护、限流和上传安全
统一 Actuator/健康检查/指标暴露策略
统一结构化日志、指标、链路追踪和告警接入策略
统一 OpenAPI 文档开关和生产保护策略
统一生产替换清单
```

可观测性要求：

- 可部署模块应引入 Actuator 或公司批准的等价健康检查能力。
- 生产环境只暴露必要端点，推荐 `health`、`info`、`prometheus`，禁止无保护暴露 `env`、`beans`、`heapdump`、`threaddump`、`configprops`。
- 日志字段必须稳定，便于日志平台、链路追踪和告警规则复用。

OpenAPI 要求：

- 开发和测试环境可以启用 OpenAPI/Swagger UI。
- 生产环境必须关闭 OpenAPI UI，或通过网关、登录态、IP 白名单等方式保护。
- OpenAPI 注解不得替代真实 DTO、校验注解和统一响应契约。

配置与密钥要求：

- 生产敏感值必须来自环境变量、配置中心或密钥系统。
- 配置项命名应稳定，CMS 和 SDK 模块对同类能力使用同一层级。
- 生成器或示例项目中的本地限流、内存 replay request store、内存幂等、日志型审计和固定密钥都只是开发占位。

扩展标准：

- 生产依赖选型按 `references/production-stack.md` 执行。
- 数据库迁移、审计表、幂等表和唯一约束按 `references/database-standard.md` 执行。
- CMS 权限码、角色、菜单、数据权限和多租户边界按 `references/authz-standard.md` 执行。
- 分层和模块依赖应使用 ArchUnit 或项目等价测试验证。
