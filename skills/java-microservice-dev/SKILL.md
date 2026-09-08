---
name: java-microservice-dev
description: Use when 需要在已有 Java/Spring Boot 项目中实现具体后端变更，包括 Controller、Service、Mapper/JPA、Feign、Redis、MQ、配置、全局异常、请求日志、参数校验、事务、幂等和测试。
---

# Java 微服务开发

使用本技能进行具体的 Java/Spring Boot 后端实现。它覆盖 API、Service、数据访问、参数校验、错误处理、日志、配置、集成客户端、MQ、Redis/缓存和测试。

优先遵循现有项目约定。已有的构建工具、包结构、响应结构、错误码模型、校验风格、数据访问技术和测试风格，优先于本技能中的默认建议。

本技能负责具体 Spring Boot 业务实现，不制定全局标准。API 契约和统一响应参考 `java-backend-api-standard`；类职责、SOLID、事务、异常、日志和测试原则参考 `java-development-principles`；模块归属不清时参考 `java-multi-module-architecture`；Netty 协议入口实现前先参考 `netty-handler-dispatcher`。

## 工作规则

- 项目没有现有构建约定时，才默认使用 Maven；如果项目使用 Gradle，则遵循 Gradle。
- 编辑前先理解模块边界；模块归属不清时使用 `java-multi-module-architecture`。
- 类职责、分层、SOLID、事务、日志和拆分判断使用 `java-development-principles`。
- 实现满足用户请求的最小可工作变更。
- 除非用户明确要求破坏性变更，否则保持 API 兼容。
- 不要引入新的框架、响应包装、数据库技术、MQ 客户端或 Redis 库，除非项目已经使用，或用户明确要求。
- 可行时，为变更行为新增或更新测试。

## 编辑前说明

编辑前简短说明：

1. 会新增或修改哪些文件。
2. 每个文件的职责。
3. 将遵循哪些现有项目模式。
4. 准备运行的验证命令。
5. 变更是否涉及 API 契约、事务、MQ、Redis、数据库、外部系统或安全行为。

## API 实现

- 保持 Controller 精简：校验 request DTO，调用 service/use-case 层，返回项目标准响应。
- 遵循项目已有统一响应类型。新项目或无本地约定时，响应字段以 `java-backend-api-standard` 为准，公开响应优先使用 `reqid/code/message/ts/data`。
- 终端或 H5 必须为每次请求生成 `x-reqid`。HTTP Controller 应将 `x-reqid` 作为必传请求头校验，并原样写入响应 `reqid`；不要在服务端为 HTTP Controller 请求静默生成 reqid。缺失其他必传请求头时仍应回显已存在的 `x-reqid`；只有 `x-reqid` 本身缺失时才用空字符串保持响应结构稳定，不得返回 `reqid: null`。
- 可用时使用 JSR-380 参数校验：
  - Spring Boot 2.x 通常使用 `javax.validation.*`。
  - Spring Boot 3.x 使用 `jakarta.validation.*`。
- 默认模板以 Spring Boot 2.x + JDK8 为基线；如果目标项目是 Spring Boot 3.x，再将 `javax.validation.*`、`javax.servlet.*` 调整为 `jakarta.validation.*`、`jakarta.servlet.*`。
- 不要在 Controller 中放业务规则、SQL、远程调用编排或重事务逻辑。
- 除非任务要求变更，否则保持现有 URL path、方法名、字段、错误码和兼容行为。

## Service 实现

- 将业务编排、事务边界、带权限感知的业务决策、幂等和状态流转放在 service/use-case 层。
- 保持 public 方法意图清晰。
- 当一个 service 开始混合业务规则、持久化协议、远程 API 协议、MQ 处理和响应格式化时，拆分协作者。
- 不要在数据库事务中执行慢远程调用，除非确实需要并已说明原因。

## 数据访问

- 遵循项目当前的数据访问技术。
- 不要在 MyBatis 项目中引入 JPA，也不要在 JPA 项目中引入 MyBatis，除非有明确需要。
- MyBatis 适合显式 SQL 和复杂/性能敏感查询。
- JPA 适合项目已经一致建模聚合并使用 repository 模式的场景。
- 保持 SQL、mapper XML、entity、DTO 和 API response 边界清晰。
- 避免 N+1 查询、无界列表加载、意外全表扫描和隐式懒加载问题。

## 事务、幂等与一致性

- 将 `@Transactional` 放在 service/use-case 方法上，不要放在 Controller。
- 保持事务尽量短。
- 避免在事务中调用远程 HTTP/RPC/MQ；如果无法避免，说明原因。
- 对重复请求或可重试操作，使用幂等键、唯一约束、请求记录或项目既有防重机制。
- DB 写入 + MQ 发布需要一致性时，遵循项目现有模式。常见方案包括：
  - transactional outbox
  - local message table
  - after-commit publish
  - scheduled compensation
  - framework-provided reliable message
- 多步骤写入要说明 rollback、retry 和 compensation 行为。

## 异常与错误映射

- 使用现有全局异常处理。如果缺失且任务需要 API 错误映射，新增聚焦的 `@RestControllerAdvice`。
- 只在需要补充业务上下文、有意恢复，或将外部错误转换为领域/应用错误时捕获异常。
- 不要吞异常。
- 不要在多层重复打印同一个异常堆栈。
- 保持错误码稳定且有意义。
- 遵循现有错误响应结构。新项目或无本地约定时，响应字段以 `java-backend-api-standard` 为准，公开响应优先使用 `reqid/code/message/ts/data`。

## 日志与链路

- 遵循现有 trace-id 和日志框架约定。
- 请求摘要日志只记录一次，包含 trace id、path、method、status 和 latency。
- 脱敏手机号、身份证号、token、凭证、密钥、签名、authorization header 和敏感 payload 字段。
- 不要记录完整响应 `data` 内容。
- 记录外部调用边界时，包含目标系统、操作、结果、耗时和脱敏标识。
- 尽量集中输出异常堆栈。

## 外部调用

- 将外部 HTTP/RPC/Feign 调用放在 `client`、`feign`、`adapter`、`gateway` 或 `integration` 包后面。
- 配置 timeout，不要依赖无限默认值。
- 在 adapter 边界将供应商特定错误转换为项目级错误。
- 只对安全幂等操作增加 retry，或遵循项目已有 retry 策略。
- 只有项目已经使用 Sentinel、Resilience4j、Hystrix 或类似工具时，才考虑 fallback、circuit breaker 或 degradation。
- 除非这是既有契约，不要把下游 DTO 直接暴露为本服务的公开 API。

## MQ 与异步处理

- 将消费者放在 `listener` 或 `consumer` 包，将生产者放在 `producer` 包或 service 层发布组件中。
- 修改 MQ 代码时，说明 topic、tag、group、payload 类型、幂等键、重试行为、死信或补偿路径。
- 消费者必须能安全处理重复消息。
- 除非项目刻意这样设计，不要复用 HTTP request/response DTO 作为 MQ payload。
- 项目支持日志和指标时，让慢外部调用和 DB 写入具备可观测性。

## Redis 与缓存

- 遵循现有 Redis 客户端和 key 命名约定。
- 新增缓存行为时，说明 key 格式、TTL、创建/读取/更新/删除点和失效策略。
- 不要把 Redis 当成隐藏事实源，除非系统已经拥有这种状态模型。
- 对分布式锁，明确 lock key、timeout、owner token、释放行为和失败处理。

## 配置

- 项目使用 typed configuration properties 时继续使用。
- 不要硬编码 URL、凭证、topic、key、端口或 timeout。
- 不要把敏感配置写入日志或样例文件。
- 对 Nacos/Apollo/Spring Cloud Config 项目，说明哪些运行时配置需要外部确认。

## 安全基线

- 校验所有外部输入。
- 在项目既有层次检查认证和授权。
- 需要时通过资源归属校验防止横向越权。
- 不要记录 secret、token、key、signature 或明文敏感数据。
- 使用参数化 SQL 或 mapper 参数；不要把不可信输入拼接进 SQL。
- 校验文件上传的大小、扩展名、content type、存储路径和权限。
- 对签名或加密请求，保持防重放、时间戳/窗口检查、nonce/幂等检查和签名校验顺序。

## 测试策略

选择能验证变更行为的最小测试：

| 变更类型 | 建议验证 |
| --- | --- |
| Controller/API 行为 | MockMvc/WebTestClient，或项目已有 API 测试模式。 |
| Service 业务规则 | JUnit + Mockito，或项目已有 test-double 风格。 |
| Mapper/repository SQL | Mapper 测试、repository 测试，或基于项目测试库的集成测试。 |
| 外部客户端 | Mock server 或 mock client 边界。 |
| MQ consumer | 基于 payload 的 listener 测试、重复消息场景、重试/错误场景。 |
| Redis/cache | key 生成、TTL、失效、锁释放行为。 |
| 事务/幂等 | 重复请求、回滚、重试和补偿测试。 |

运行相关编译和测试：

```bash
mvn -q -DskipTests compile
mvn test -pl <module> -DskipTests=false
mvn clean package -pl <module> -am -DskipTests
```

Gradle 项目使用现有 Gradle wrapper 和等价模块任务。

如果 DB、MQ、Nacos、Redis、私有 Maven 仓库或外部服务不可用，说明阻塞原因，并运行最近似的静态或模块级验证。

修改本技能后运行：

```powershell
py "D:\Users\CodexData\.codex\skills\java-microservice-dev\scripts\check_java_microservice_dev_skill.py"
py "D:\Users\CodexData\.codex\skills\java-microservice-dev\scripts\run_forward_tests.py"
```

前向验证场景位于 `references/forward-test-scenarios.md`；维护本技能后可用 `scripts/run_forward_tests.py --prompts` 输出场景 prompt，用 `--score-output`、`--score-dir` 或 `--score-fixtures` 对真实输出做 keyword scoring。

## 实现模板

仅在项目缺少本地模式时使用模板：

- `templates/controller.java`
- `templates/service.java`
- `templates/global-exception-handler.java`
- `templates/api-response.java`
- `templates/error-code.java`
- `templates/common-error-code.java`
- `templates/junit-service-test.java`
- `templates/mybatis-mapper.java`
- `templates/mybatis-mapper.xml`
- `templates/entity.java`
- `templates/feign-client.java`
- `templates/external-adapter.java`
- `templates/rocketmq-consumer.java`
- `templates/rocketmq-producer.java`
- `templates/message-payload.java`
- `templates/redis-key.java`
- `templates/cache-service.java`
- `templates/distributed-lock-service.java`

不要把模板盲目复制到已经有成熟约定的项目中。

## 输出契约

任务完成时提供：

1. 变更文件和每个文件的职责。
2. 行为影响和兼容性影响。
3. 已运行的验证命令。
4. 风险、外部依赖或后续事项。
