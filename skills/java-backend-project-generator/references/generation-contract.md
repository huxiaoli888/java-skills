# 生成项目契约

本文件记录 `java-backend-project-generator` 生成项目必须满足的详细契约。普通生成任务优先运行脚本；当需要解释生成内容、修改 base-template、调整 profile 裁剪或评估生成结果合规性时，读取本文件。

## 0. 版本边界

- 当前 base-template 使用 `record`、`String.isBlank()` 和 `jakarta.*` 包，只支持 Java 17+。
- 当前 base-template 只支持 Spring Boot 3.x/4.x，不支持 Spring Boot 2.x 或 JDK8。
- 如果用户需要 Spring Boot 2.x 或 JDK8，应使用既有项目实现技能 `java-microservice-dev` 的 Boot2/JDK8 模板，而不是通过本生成器覆盖低版本参数。

## 0.1 Profile 定位

- `minimal` 是默认 profile，目标是 renren 风格轻量后台框架，优先保证 CMS 后台接口、统一响应、异常、基础鉴权、访问日志、健康检查和后续后台管理闭环可演进。
- `standard` 是显式启用的增强 profile，目标是 CMS/SDK 双入口和开放接口规范，才默认包含 `sdk-api`、SDK 签名防重放、SDK 冒烟脚本和开放接口文档。
- `-IncludeNetty` 是独立开关，不属于默认后台框架；只有用户明确要求 TCP、UDP、长连接或 Netty 协议入口时才追加生成。
- 当前 `minimal` 仍复用完整模板裁剪得到；已包含开发级 CMS 登录/token、`cms.sys` 用户/角色/菜单/权限/字典/参数查询骨架、操作审计落库、操作日志查询和登录日志查询骨架。后续优化方向是补齐生产级 RBAC 治理能力，同时避免默认生成 SDK/Netty/开放平台管理能力。

## 1. 所有 Profile 必须包含

- 配置 UTF-8 的 Maven 父工程。
- `common` 和 `cms-api` 模块；`standard` profile 还必须包含 `sdk-api` 模块。
- 当生成命令启用 `-IncludeNetty`，还必须包含 `{projectName}-netty` 模块；默认 `minimal` 和 `standard` 不包含 Netty 模块。
- 根目录和模块级 `AGENTS.md`。
- 架构、开发和 API 清单文档。
- 配置说明文档。
- 生产技术栈、数据库/迁移、CMS 授权/数据权限文档。
- API 生命周期、错误码治理、文件上传生产化、韧性和可观测性文档。
- 每个可部署 API 模块必须包含 `application.yml`、`application-dev.yml`、`application-test.yml` 和 `application-prod.yml`。
- 统一响应报文：`reqid/code/message/ts/data`。
- 前端或客户端必须通过请求头 `x-reqid` 传入请求唯一编号；生成的 HTTP 响应必须包含同一个 `reqid`。HTTP 请求缺失 `x-reqid` 时，错误响应使用空字符串保持结构稳定，不生成服务端 reqid，也不得返回 `reqid: null`。
- 字符串错误码：`000000`、`AC0001` 到 `AC0011`、`AC9999`。
- `ErrorCode` 和 `CommonErrorCode` 必须放在 `common.code` 包；`common.exception` 只放异常、全局异常处理和字段错误对象，不要继续使用 `common.error` 承载错误码。
- 全局异常映射。
- 单个全局 trace/访问日志过滤器，记录脱敏后的请求体、请求时间、响应时间、响应 `code/message`，不记录响应体、token、签名或密钥值。
- 请求体日志必须经过可复用脱敏策略；默认不脱敏 `x-udid` 和 `x-api-key`。
- 操作审计模板必须包含注解、记录对象、服务接口、基于日志的默认实现和 AOP 切面，并按职责放在 `common.log.annotation`、`common.log.model`、`common.log.service`、`common.log.aspect`；CMS 模块必须提供 `OperationAuditService` 的数据库实现，将后台操作审计写入 `cms_operation_log`，同时保留 `cms_login_log` 登录日志表和查询骨架。
- CMS 授权模板必须包含 `RequirePermission`、`PermissionEvaluator`、`PermissionAuthorizationAspect`、`PrincipalContext`、`TenantContext` 和 `DataPermissionContext`，并按职责放在 `common.permission.annotation`、`common.permission.service`、`common.permission.aspect`、`common.permission.context`、`common.permission.model`；生成的 CMS filter 可以填充当前主体，但不得硬编码真实 RBAC 策略。
- 共享 CORS 模板必须包含 `ApiCorsConfiguration` 和 `ApiCorsProperties`，使用明确 origin；允许凭证时不得使用通配 origin。
- SQL 注入防护模板必须包含 `SqlInjectionGuard`、`SqlInjectionFilter`、`SqlInjectionProperties` 和 `SqlInjectionConfiguration`；filter 只检查 query string 和可选表单参数，Mapper 代码仍必须使用参数绑定和动态字段白名单。
- 限流模板必须包含 `RateLimitProperties`、`RateLimitConfiguration`、`RateLimitFilter`、`RateLimiter` 和 `InMemoryRateLimiter`；内存实现仅用于开发，生产应使用网关或 Redis/分布式限流。
- 文件上传安全模板必须包含 `FileUploadSecurityProperties`、`FileUploadSecurityConfiguration` 和 `FileUploadSecurityPolicy`；生产应增加对象存储、魔数校验、杀毒/内容扫描和受权限控制的 URL。
- 远程调用必须文档化超时、重试、熔断、outbox 和事务边界规则；只有幂等操作允许重试。
- 每个可部署模块必须包含 Actuator 或等价健康检查能力。生产暴露范围必须最小化，且不得无保护暴露敏感诊断端点。
- 可部署模块必须包含结构化日志、Actuator/Prometheus 指标、trace id 传播和生产端点暴露策略等可观测性模板。
- OpenAPI/Swagger UI 是可选项；如果生成，生产环境必须禁用或受保护。
- common 模块测试模板必须包含 ArchUnit 分层/Controller 契约测试，以及 CORS、SQL 注入、限流、文件上传和异常契约测试。
- 可部署 API 模块测试模板必须包含生产配置策略测试。
- 根目录脚本必须包含 `scripts/smoke-test.ps1`。`minimal` profile 只构建、启动和验证 CMS API；`standard` profile 构建项目、启动 CMS/SDK API jar、检查健康、调用 CMS 分页和 SDK 创建/查询 API、验证 `code=000000`，并且只停止它自己启动的进程。
- `common` 中必须包含共享签名认证支持和 `SignatureCanonicalPayload`，统一处理 GET query、POST JSON raw body 和 CMS form-urlencoded body 的签名输入。
- 通用请求头包含 `authorization`、`accept-language`、`x-trace-id`、`x-reqid`、`x-timestamp`、`x-sign`、`x-sign-alg`、`x-api-version` 和 `x-udid`。
- CMS security filter 对受保护路径要求 `authorization: Bearer <token>`、`x-udid`、`x-reqid`、`x-timestamp`、`x-sign`、`x-sign-alg` 和 `x-api-version`，支持可配置 `auth-exclude-paths` 和 `udid-exclude-paths`，且不得要求 `x-api-key`。
- CMS 受保护接口必须同时支持 GET 签名、POST `application/json` 签名和 POST `application/x-www-form-urlencoded` 表单签名；GET query 按 URL encoded key/value 规范排序后参与签名，JSON body 和 form body 都使用原始 HTTP body bytes，不解析后重新排序、重新编码或重新拼接。
- CMS 模块默认配置不得要求 `x-api-key`；CMS 的 CORS allowed headers 默认包含 `authorization`、`accept-language`、`content-type`、`x-trace-id`、`x-udid`、`x-reqid`、`x-timestamp`、`x-sign`、`x-sign-alg` 和 `x-api-version`。

## 2. Standard Profile 额外契约

- SDK security filter 也必须支持可配置 `auth-exclude-paths`；除非路径匹配可配置 `udid-exclude-paths`，否则在签名认证前先检查 `x-udid`。
- SDK security filter 支持 GET query 签名和 POST `application/json` raw body 签名，不要求支持 form-urlencoded 表单签名。
- 单个 SDK security filter 负责请求体缓存、`x-sign` 签名验证、时间戳窗口校验，以及 `x-api-key + x-reqid` 防重放。
- SDK 签名 canonical 必须覆盖 `x-udid`，避免设备或用户唯一标识被篡改后仍通过签名校验。
- SDK 默认示例采用 renren 风格轻量分层：`controller/dto.request/dto.response/service/service.impl`；不得默认生成 `command`、`model`、`CommandService`、`QueryService`。只有用户明确要求复杂交易、状态机或领域建模时，才在业务模块内新增命令或领域模型。

## 3. 可选 Netty 模块契约

当用户明确要求 TCP 长连接、UDP、Netty 协议入口或类似“长连接服务”时，生成器必须启用 `-IncludeNetty`，并在当前 profile 基础上追加 `{projectName}-netty` 模块。

Netty 模块必须满足：

- 模块命名默认为 `{projectName}-netty`，可通过 `-NettyModuleName` 覆盖。
- 模块依赖 `common`，不得依赖 `cms-api` 或 `sdk-api`。
- 模块包含独立 Spring Boot 启动类和 `application.yml`、`application-dev.yml`、`application-test.yml`、`application-prod.yml`。
- 默认 HTTP 管理端口为 `18082`，TCP 端口为 `19090`，UDP 端口为 `19091`，均可通过生成参数覆盖。
- TCP 请求使用 JSON 行帧；UDP 请求使用单个 datagram JSON；两者共用统一报文封装。
- 请求 envelope 顶层字段包含 `reqid`、`func`、`version`、`ts`、`udid`、`authorization`、`sign`、`sign-alg`、`api-key` 和 `payload`。
- `seqno` 只作为 `payload` 内的业务顺序字段，用于同一连接或同一设备的业务顺序控制，不替代 `reqid`。
- 响应必须复用 common 的统一返回码语义，返回 `reqid/code/message/ts/data`。
- Netty 无法解析请求、请求缺失 `reqid` 或服务端主动响应时，响应使用 `server-UUID` 形式的服务端唯一 `reqid`，不得返回空字符串或 JSON null。
- 必须包含 AUTH 和 HEARTBEAT 基础 handler，心跳成功返回 ACK。
- 必须包含 `func + version` handler dispatcher，不允许把所有协议处理堆在一个 Netty handler 中。
- 必须包含基础鉴权防篡改入口，检查 `udid`、`reqid`、`ts`、`sign`、`sign-alg`、`api-key` 或 `authorization` 等字段；模板实现可以是开发占位，但必须明确生产要替换为真实 HMAC/RSA 验签和分布式防重放。
- 必须包含 TCP/UDP 全局日志，记录 `reqid`、`func`、`version`、`udid`、远端地址、耗时和返回码，不得记录 token、签名、密钥和明文敏感 payload。
- TCP/UDP handler 必须区分可预期协议格式错误和不可预期程序异常：JSON 解析或字段格式错误返回 `AC0001` 并使用 `log.info` 记录 `protocol_invalid`；真正程序异常必须先使用 `log.error` 记录脱敏堆栈，再尝试返回兜底错误码，避免兜底响应写出失败时丢失原始异常。
- 必须包含基础测试，至少覆盖 dispatcher 路由、AUTH、HEARTBEAT 和统一响应。
- 生成后必须通过 `check_java_api_standard.py`，并能执行 `mvn -q -pl {projectName}-netty -am -DskipTests compile`。

Netty 模块不做：

- 不默认生成 WebSocket 长连接入口，除非后续模板明确支持。
- 不在模板中实现真实生产密钥管理、分布式 replay store、分布式限流和连接集群治理。
- 不把 TCP/UDP 协议业务 handler 放进 `common`。

## 4. 所有 Profile 的实现规则

- 业务幂等骨架基于业务请求字段，例如 `requestNo` 或 `businessNo`；不要生成 `idempotencyKey` 请求头或公共参数。
- 数据库和幂等文档必须说明迁移脚本、操作审计存储、幂等存储和业务唯一约束。
- 持久化模板必须包含 `BaseEntity`、`OperatorContext`、`EntityAuditFillSupport` 和逻辑删除常量；实体主键由 MyBatis-Plus `@TableId(type = IdType.ASSIGN_ID)` 生成，`EntityAuditFillSupport` 只填充审计字段，不手动生成 `id`。
- 业务表标准字段为 `id/create_by/create_time/modify_by/modify_time/version/deleted`；`version` 表示乐观锁版本，`deleted=0` 表示正常，`deleted=-1` 表示删除。
- HTTP filter 可以根据 `x-udid` 或 `x-api-key` 填充 operator context，但数据库审计字段必须由持久化层支持、ORM 审计、mapper 拦截器或 repository 基类填充，而不是由 filter 直接写数据库。
- 生成的文档/模板必须包含 MyBatis-Plus CRUD 模板、面向 H2/MySQL 的 CRUD 集成测试模板、Redis 防重放/限流生产替换、Redis/JDBC 集成测试模板、JDBC 幂等/审计替换模板、生产替换自动配置/测试模板和版本兼容指导。
- `-IncludeDbCrudExample` 为可选开启项。启用后，生成器会用 CMS 模块中的 MyBatis-Plus CRUD 示例替换默认内存 CMS sample item，并增加必要的测试/数据库依赖。
- DTO/VO/Entity 可以使用 Lombok，但优先使用 `@Getter/@Setter` 而不是 `@Data`；不要使用 Lombok `@ToString` 暴露 token、secret、password、authorization 或 signature 字段。
- request DTO 和 response DTO 默认分开；只有字段含义、校验规则、展示规则和生命周期完全一致时，才允许复用轻量 DTO，禁止用 entity 充当接口入参或出参。
- 默认 CMS 包结构使用大域分包，例如 `cms.sys.controller/service/mapper/entity/dto.request/dto.response`；不要按用户、角色、菜单等小对象创建过多顶层业务包。
- 默认 SDK 包结构使用轻量分包，例如 `sdk.testtask.controller/service/service.impl/dto.request/dto.response`；不要默认生成 CQRS 风格 `command/model` 包。
- 复杂 SQL 参考 renren 项目做法，通过 `src/main/resources/mapper/**/*.xml` 实现；Java Mapper 接口只保留方法签名和参数声明。
- CMS 授权文档必须说明权限码、角色、菜单、数据权限、租户边界和审计要求。
- 可观测性文档必须说明访问日志字段、指标标签基数、trace 传播、JSON/key-value 日志和危险 Actuator 端点限制。
- API 生命周期文档必须说明版本、废弃、兼容窗口、错误码冻结和契约测试。
- `minimal` profile 的 P0 样例 API 骨架：
  - CMS 分页查询测试任务
  - CMS 获取任务详情
  - CMS sample item CRUD：创建、分页、详情、更新、删除
- `standard` profile 的 P0 样例 API 骨架：
  - SDK 创建测试任务
  - SDK 查询任务状态
  - CMS 分页查询测试任务
  - CMS 获取任务详情
  - CMS sample item CRUD：创建、分页、详情、更新、删除
- SDK 调用方应用、SDK 密钥、SDK 调用日志查询属于可选开放平台管理能力，不属于默认 P0 骨架。
- `minimal` profile 生成文档、冒烟脚本和模块清单不得继续承诺存在 `sdk-api`、SDK 调用方或 `x-api-key`。
