# Java 后端 API 标准检查清单




## 目录

- [1. 新项目标准检查清单](#1-新项目标准检查清单)
- [2. API 评审检查清单](#2-api-评审检查清单)
- [3. 高风险交易检查清单](#3-高风险交易检查清单)
- [4. 自动化静态检查](#4-自动化静态检查)
- [5. Codex 最终回复检查清单](#5-codex-最终回复检查清单)

## 1. 新项目标准检查清单

项目分类：

- 已识别 API 使用方：后台、H5、移动端、合作方、回调、内部服务。
- 已选择并记录安全档位。
- 已选择 API 版本策略。
- 已定义 API 废弃策略、错误码冻结规则和契约测试范围。
- 已选择并记录公司级生产技术栈，且 Spring Boot、Spring Cloud、Nacos、MyBatis-Plus 等依赖兼容。
- 源码使用 UTF-8 编码。
- 已拆分 `application.yml`、`application-dev.yml`、`application-test.yml`、`application-prod.yml`。
- 已编写配置说明文档，覆盖端口、context-path、安全、CORS、SQL 注入、防重放、幂等和生产替换项。

项目结构：

- Controller、service、repository/mapper、entity、DTO、converter、config、security 和 common 包已分离。
- Request DTO 和 response DTO 不是持久化 entity。
- 公共响应和错误类不依赖业务模块。
- 事务由 service/application 方法持有。
- 如需要 TCP 长连接或 UDP，已新增 `{project}-netty` 模块，且只依赖 common，不依赖 cms-api 或 sdk-api。
- 已提供 ArchUnit 或等价架构测试，验证当前 profile 的模块依赖方向；`standard` 验证 common/cms-api/sdk-api 依赖方向以及 CMS/SDK API 模块互不依赖，`minimal` 验证 common/cms-api 依赖方向且不残留 sdk-api 模块承诺。

数据库：

- 已选择 Flyway、Liquibase 或公司批准的迁移方式。
- 操作审计表、幂等表和关键业务唯一约束已设计。
- 已提供 `BaseEntity`、`OperatorContext`、`EntityAuditFillSupport` 和逻辑删除常量，或项目已有等价实现；MyBatis-Plus 项目中 `id` 使用 `@TableId(type = IdType.ASSIGN_ID)`，审计填充不手动生成 `id`。
- 如果使用 MyBatis-Plus，`BaseEntity.version` 已配置 `@Version`，common 模块已引入 `mybatis-plus-annotation`，拥有数据库访问的 API 模块已配置 `MybatisPlusInterceptor` 和 `OptimisticLockerInnerInterceptor`。
- 业务表统一字段 `id/create_by/create_time/modify_by/modify_time/version/deleted` 已设计，且 `deleted=0/-1` 语义明确。
- 订单、支付、回调等高风险表已定义业务唯一约束和状态校验字段。
- Mapper 动态字段、排序字段和数据权限字段使用服务端白名单。
- 复杂 SQL 参考 renren 项目做法，已放在 `src/main/resources/mapper/**/*.xml`，Java 代码中没有拼接长 SQL。

API 契约：

- 每个 endpoint 返回 `ApiResult<T>`。
- 分页使用统一 `PageResult<T>`。
- 内存分页或样例分页使用 `PageSupport`，数据库分页保持同一页码语义。
- 错误码遵循中心化枚举或注册表。
- 参数校验错误使用相同响应包装。
- 响应中存在 `reqid` 和 `ts`；`traceId` 保留在日志和内部链路追踪上下文中。
- 生成 API 文档时，OpenAPI 注解与真实请求/响应对象一致。

安全：

- 需要认证的接口已强制认证。
- CMS/API 模块存在时，已生成对应安全组件；`standard` 需要 `CmsSecurityFilter`、`CmsSecurityProperties`、`SdkSecurityFilter`、`SdkSecurityProperties`，`minimal` 只要求 CMS 安全组件。
- CMS 后台权限已具备 `RequirePermission`、`PermissionEvaluator`、`PermissionAuthorizationAspect` 和主体上下文，且受保护接口不只依赖前端菜单隐藏。
- `auth-exclude-paths` 和 `udid-exclude-paths` 已区分配置。
- 受保护资源已检查授权。
- 敏感 API 已定义小写公共请求头、防重放和防篡改要求。
- 可重试写接口已定义业务幂等行为。
- 已配置请求大小、分页大小和上传大小限制。
- 已配置统一 CORS，生产环境没有在携带凭证时使用 `*` 来源。
- 已配置 SQL 注入防护策略：入口轻量拦截、动态字段白名单、Mapper XML 参数绑定。
- 已配置限流能力，登录、验证码、导出、下单、支付、回调等敏感接口有明确规则。
- 已配置文件上传安全能力，包含大小、扩展名、content type 和生产扫描/对象存储替换要求。
- 已定义远程调用超时、重试、熔断、outbox 和高风险写操作的事务边界。
- 已配置 Actuator 或等价健康检查能力，生产只暴露必要端点。
- 已配置 OpenAPI 开关，生产环境关闭或受保护。
- CMS 权限码、角色、菜单和数据权限已定义，前端菜单隐藏不作为后端授权依据。
- 多租户和数据权限已通过 `TenantContext`、`DataPermissionContext` 或等价服务端上下文生成，不信任客户端传入范围。
- 多租户或开放平台调用方身份不信任客户端 body/query 中的 `tenantId`。
- Netty TCP/UDP/WebSocket 入口已按 `netty-transport-standard.md` 定义 envelope、鉴权、防篡改、防重放、心跳、ACK 和统一响应。

日志：

- 访问日志包含 trace id、reqid、身份、path、HTTP status、响应 code、message、requestTime、responseTime、duration、clientIp 和 requestBody。
- 请求体写日志前已通过 `RequestBodyMasker` 或等价策略脱敏。
- 敏感字段已脱敏。
- 已配置结构化日志、Actuator/Prometheus 指标、trace id 传播和生产危险端点禁用策略。
- 新增、修改、删除、导入、导出、权限、支付和配置操作已审计。
- 后台敏感操作已使用 `OperationAudit` 或等价审计注解/AOP。

测试：

- 全局异常处理器有测试。
- 参数校验失败有测试。
- 认证/授权失败有测试。
- 启用 MyBatis-Plus CRUD 示例时，至少有 H2 或 MySQL 集成测试覆盖 mapper 插入查询、乐观锁和逻辑删除。
- 启用生产替换实现时，至少有 Redis replay/限流集成测试和 JDBC 幂等/审计集成测试；外部 Redis 可通过环境变量或测试容器启用。
- 启用签名、防重放和幂等时，对应路径有测试。
- CORS、SQL 注入、限流、文件上传和生产配置策略有测试。
- 分层依赖和 Controller 契约有 ArchUnit 或等价测试。
- Controller 测试验证统一响应格式。
- 如生成或实现 Netty 模块，已测试 `AUTH`、`HEARTBEAT`、ACK、handler registry、签名失败、重放请求、鉴权超时和统一错误响应。

## 2. API 评审检查清单

逐个 endpoint 验证：

- 路由和 HTTP 方法与操作语义匹配。
- 请求对象是 request DTO，不是 entity。
- 响应对象是 response DTO，不是 entity。
- endpoint 返回统一响应包装。
- 必填、长度、范围、格式和枚举约束都有校验注解。
- 正常业务失败使用稳定错误码和统一响应，不通过异常作为常规控制流，不打印 `error` 堆栈。
- endpoint 不暴露堆栈或内部异常消息。
- endpoint 有清晰授权规则。
- 敏感写接口定义了幂等和防重放行为。
- 日志包含足够追踪信息，但不暴露密钥和隐私。

## 3. 高风险交易检查清单

适用于订单、支付、退款、钱包、回调和对账 API：

- 金额类型安全。
- 状态流转明确且已校验。
- 通过业务唯一键和唯一约束阻止重复请求。
- 外部回调在状态变更前完成签名验证。
- 重试行为已文档化。
- 失败状态可对账。
- 审计记录不会静默丢失。
- 数据库事务边界清晰。
- 远程调用没有在无说明的情况下隐藏于长数据库事务中。
- 已按 `references/production-replacement.md` 替换固定密钥、内存 replay request store、内存幂等、日志型审计和示例权限实现。
- 已按 `references/database-standard.md` 验证幂等表、业务唯一约束和状态流转条件。
- 已按 `references/authz-standard.md` 验证后台权限、数据权限和多租户边界。

## 4. 自动化静态检查

验证生成项目或现有 Java 项目时运行：

```text
scripts/check_java_api_standard.py <project-root> --profile standard --fail-on-error
```

按生成器 profile 选择 `--profile minimal` 或 `--profile standard`；生产增强路线图当前不是 checker profile，也不是生成器脚本参数。默认使用 `--fail-on-error`，避免自动化流程忽略 ERROR 级别问题；如只做人工预览，可去掉该参数。

检查器规则 ID、自动覆盖范围和人工检查边界见 `checker-coverage-matrix.md`。当新增或修改 checker 规则时，必须同步更新覆盖矩阵并补充负向 fixture。

脚本检查：

- 缺少公共 API 基础设施类。
- 缺少 `PageSupport`、持久化审计字段填充基础件或雪花 ID 生成器。
- 缺少请求体缓存、访问日志、统一安全错误响应等公共过滤器基础设施。
- 缺少请求体脱敏策略或操作审计基础设施。
- 缺少 ArchUnit 或等价架构测试。
- Controller 看起来没有返回 `ApiResult<T>`。
- Controller 导入 entity 包。
- Request DTO 校验消息未使用 i18n key。
- 明显违反分层的依赖。
- Maven POM 中仍存在默认 `core` 模块，或 `cms-api/sdk-api` 依赖旧 `core`。
- `minimal` profile 仍存在 sdk-api 模块，或文档/脚本继续承诺 sdk-api。
- `common` 中出现业务 mapper、entity、repository 或易变 service 实现。
- 后台接口疑似把 `x-api-key` 当作管理后台公参。
- 签名头常量、访问日志字段或 `x-udid` 规则与标准不一致。
- 高风险订单/支付/回调 API 没有可见签名、防重放或幂等支持。
- 缺少统一 CORS 配置或 CORS 配置存在危险组合。
- 缺少 SQL 注入防护能力，或 Mapper 存在明显 `${}` 风险。
- 缺少限流能力或限流配置。
- 缺少文件上传安全能力。
- 生产 Actuator 暴露范围过大。
- 缺少关键生产标准文档、数据库迁移说明或权限标准说明。
- 缺少 `application-dev.yml`、`application-test.yml` 或 `application-prod.yml`。
- 生产配置中存在默认 token、默认 apiKey/secret 或危险 CORS 配置。

脚本发现是信号，不是最终结论。修改稳定代码前，需要人工确认框架特定模式。

## 5. Codex 最终回复检查清单

使用本技能时，最终回复应包含：

- 创建或修改的文件。
- 应用了哪些 API 标准。
- 选择了哪个安全档位。
- 运行了哪些测试或验证。
- 哪些标准由于项目缺少上下文而无法应用。
