# Java 后端项目一键生成工作流

## 1. 目标

该工作流用于新建 Java/Spring Boot 多模块后端项目。目标不是只生成 Maven 空壳，而是一次性生成接口侧项目基础设施，避免后续逐步追问：

```text
接口清单 -> DTO/controller -> 签名 -> 防重放 -> 幂等 -> 全局日志
```

## 2. Profile 与模块

默认 profile 为 `standard`。需要小型内部后台骨架时使用 `-Profile minimal`，详细裁剪规则见 `profile-design.md`。

| 模块 | 是否可部署 | 职责 |
| --- | --- | --- |
| `{projectName}-common` | 否 | 统一响应、分页、错误码、异常、trace、访问日志、签名工具、防重放和幂等接口 |
| `{projectName}-cms-api` | 是 | 后台/CMS HTTP API 入口、CMS DTO、开发级登录/token、后台认证和审计入口 |
| `{projectName}-sdk-api` | 是，仅 standard | 对外 SDK/OpenAPI HTTP 入口、签名、防重放、SDK DTO |

默认不生成 `{projectName}-core`。数据库调用、mapper、entity、repository 和事务边界放在实际调用数据库的 API 模块中；只有确认存在稳定共享业务能力时，才新增独立业务库模块。

## 3. 生成内容

一键生成必须包含：

- 父 POM 和子模块 POM。
- UTF-8 `.editorconfig`、`.gitattributes`。
- 根与模块级 `AGENTS.md`。
- `docs/architecture/module_map.md`。
- `docs/architecture/system_architecture.md`。
- `docs/development/module_development_guide.md`。
- `docs/development/configuration_guide.md`。
- `docs/development/production_stack.md`。
- `docs/development/database_standard.md`。
- `docs/development/permission_standard.md`。
- `docs/api/api_inventory.md`。
- 当前 profile 中每个可部署模块的 `application.yml`、`application-dev.yml`、`application-test.yml`、`application-prod.yml`。
- 统一 `ApiResult<T>`。
- 统一 `PageResult<T>`。
- `ErrorCode` 和 `CommonErrorCode`。
- `BusinessException` 和 `GlobalExceptionHandler`。
- `RequestTraceLogFilter`、`RequestBodyMasker` 和对应配置。
- `common.log.annotation.OperationAudit`、`common.log.model.OperationAuditRecord/OperationType`、`common.log.service.OperationAuditService/LoggingOperationAuditService`、`common.log.aspect.OperationAuditAspect` 操作审计模板。
- CMS 模块默认包含开发级 `cms_sys_user`、`cms_sys_role`、`cms_sys_menu`、`cms_sys_dict`、`cms_sys_dict_item`、`cms_sys_param`、`cms_operation_log`、`cms_login_log` 迁移脚本、Mapper XML、Service 和查询 Controller；`common` 的日志型审计实现只作为没有业务模块实现时的兜底。
- `ApiCorsConfiguration`、`ApiCorsProperties` 统一跨域模板，生产环境必须配置明确来源，携带凭证时禁止 `*`。
- `SqlInjectionGuard`、`SqlInjectionFilter`、`SqlInjectionProperties`、`SqlInjectionConfiguration` SQL 注入防护模板；filter 只检查 query string 和可选 form 参数，Mapper 仍必须使用参数绑定和动态字段白名单。
- `RateLimitProperties`、`RateLimitConfiguration`、`RateLimitFilter`、`RateLimiter`、`InMemoryRateLimiter` 限流模板；内存实现仅用于开发，生产应替换为网关或 Redis/分布式限流。
- `FileUploadSecurityProperties`、`FileUploadSecurityConfiguration`、`FileUploadSecurityPolicy` 文件上传安全模板；生产应补对象存储、魔数校验、杀毒/内容扫描和权限化 URL。
- API 模块引入 Actuator，用于健康检查、指标和探针；生产只暴露必要端点。
- 保留 OpenAPI 配置片段，开发/测试可启用，生产必须关闭或受保护。
- `LayerDependencyArchTest`、`ControllerContractArchTest` 分层和 Controller 契约测试。
- CORS、SQL 注入、限流、文件上传、异常和生产配置策略测试模板。
- common 复用型 query/body/form 签名鉴权支持。
- CMS `CmsSecurityFilter`，受保护路径支持 Bearer token + x-udid，登录、验证码、探活等路径可通过 `auth-exclude-paths` 排除整体鉴权，也可通过 `udid-exclude-paths` 仅排除 x-udid 前置校验，不要求 x-api-key。
- `standard` profile 生成 SDK `SdkSecurityFilter`，命中 `auth-exclude-paths` 的路径跳过签名鉴权；未命中 `udid-exclude-paths` 的路径先校验 x-udid，再进入签名鉴权。
- `standard` profile 生成 SDK `SdkSecurityFilter`，在单个 filter 内完成请求体缓存、GET query/POST JSON 签名验签、时间窗口和防重放。
- `standard` profile 生成 SDK 配置化 `apiKey/secret` 占位解析器。
- 内存版 replay request 存储。
- 内存版业务幂等存储。
- P0 示例接口骨架。

默认生成后台日志数据库 schema；不默认生成真实业务表 schema。数据库标准文档必须说明迁移脚本、操作审计表、登录日志表、幂等表、业务唯一约束和 SQL 安全规则。

不默认生成 CMS 侧 SDK 调用方应用、SDK 密钥、SDK 调用日志等开放平台管理包。只有用户明确要求“开放平台管理后台”或“SDK 调用方管理”时，才在 CMS 模块中新增独立大域，例如 `cms.openapi` 或 `cms.sdkmanage`。

## 4. 安全默认值

所有接口通用请求头：

```text
authorization
accept-language
x-trace-id
x-udid
x-reqid
x-timestamp
x-sign
x-sign-alg
x-api-version
```

CMS 默认启用登录态认证：

```text
authorization: Bearer <token>
x-udid
```

CMS 默认 CORS allowed headers 只声明：

```text
authorization
accept-language
content-type
x-timestamp
x-reqid
x-sign
x-sign-alg
x-api-version
x-trace-id
x-udid
```

SDK/OpenAPI 默认启用：

```text
x-api-key
```

签名输入：

```text
UTF8(
  METHOD + "\n" +
  PATH + "\n" +
  CANONICAL_QUERY + "\n" +
  TIMESTAMP + "\n" +
  REQID + "\n" +
  API_KEY + "\n" +
  UDID + "\n" +
  SIGNATURE_ALG + "\n" +
  API_VERSION + "\n"
) + RAW_BODY_BYTES
```

签名 payload 规则：

- GET 请求 body 为空，query 使用 URL encoded key/value 规范排序。
- SDK POST JSON 使用实际发送的 raw body 字节参与签名。
- CMS POST JSON 使用实际发送的 raw body 字节参与签名。
- CMS POST `application/x-www-form-urlencoded` 使用原始 form body bytes 参与签名，不解析后重新排序、重新编码或重新拼接。
- SDK 不要求支持 form-urlencoded 签名；不要把 SDK 表单提交误当成标准能力。

签名结果放在 `x-sign` 中；`authorization` 只承载登录后的 token。

## 5. 幂等默认值

不生成公共 `idempotencyKey` 请求头或公参。

业务幂等使用业务报文字段：

```text
requestNo
businessNo
orderNo
paymentNo
callbackNo
```

默认示例使用：

```text
businessType = TEST_TASK_CREATE
businessKey = businessNo 优先，否则 requestNo
```

## 6. 生产替换项

生成项目后必须替换：

- 默认开发管理员、CMS 签名密钥、SDK `apiKey/secret`。
- 内存请求重放存储，生产建议 Redis 或等价高速存储，键建议使用 `x-api-key + x-reqid` 或 CMS token 指纹加 `x-udid + x-reqid`。
- 内存幂等存储，生产建议数据库唯一约束 + 结果快照或结果引用。
- CMS 生产级用户、角色、菜单、权限和密码策略。
- SDK 调用方密钥来源，生产建议数据库、配置中心或开放平台管理系统。
- P0 示例接口的内存服务实现，替换为真实 repository/mapper/entity。
- 内存限流实现，替换为网关限流或 Redis/分布式服务端兜底限流。
- 文件上传基础校验，替换或增强为对象存储、魔数校验、杀毒/内容扫描和权限化访问。
- Actuator 生产暴露范围，确认只开放 `health`、`info`、`prometheus` 等必要端点。
- OpenAPI/Swagger UI，生产环境关闭或加网关/登录态/IP 白名单保护。
- CMS 默认开发管理员、开发级 `cms.sys` 种子数据和 super admin 权限，替换为真实登录、权限码、角色、菜单和数据权限体系。
- 数据库幂等和审计文档中的占位设计，替换为项目实际迁移脚本和表结构。
