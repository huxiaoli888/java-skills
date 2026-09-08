---
name: java-backend-api-standard
description: Use when Java/Spring Boot 任务需要定义或检查 HTTP/API 契约、统一响应、错误码、reqid、请求头、参数校验、认证鉴权、签名、防重放、幂等、分页、OpenAPI 或 API 静态合规；具体实现、脚手架、多模块和 Netty 协议细节由对应专项 skill 承接。
---

# Java 后端 API 标准

## 概述

本技能是 HTTP/API 契约的权威来源。其他 Java/Netty skill 中涉及统一响应、错误码、`reqid`、`status`、请求头、鉴权、签名、防重放、防篡改和幂等时，只保留摘要并引用本技能，不重新定义详细规则。

当 Java 后端项目需要统一的前后端分离 API 契约和分层结构时，使用本技能。输出目标不是单纯生成接口文档，而是定义规则限制、评审现有实现或检查生成结果。

本技能把 API 标准视为工程约束：在新增 controller 之前，必须先设计请求/响应结构、错误码、DTO 边界、参数校验、安全、日志、幂等和包分层。

## 适用场景

- 定义新的 Java/Spring Boot 后端标准规则。
- 定义前后端分离项目必须遵守的 API 规则。
- 评审现有 Java 后端是否符合统一接口标准。
- 新增暴露 HTTP API 的模块，并要求匹配项目级契约。
- 设计后台管理、移动端、H5、开放平台、订单、支付或回调 API。
- 设计 TCP 长连接、UDP 私有协议或 Netty WebSocket 入口，并要求复用统一鉴权、防篡改、错误码、日志和分层标准。

不要只为了生成 API 文档而使用本技能。本技能用于定义后端实现标准，接口文档应当遵守该实现标准。

## 工作流程

1. 对项目和 API 使用方分类。
   - 内部后台管理控制台
   - 移动端或 H5 客户端
   - 第三方开放平台
   - 订单、支付、回调或其他高风险交易服务

2. 选择安全档位。
   - 基础内部 API：前端必须通过 `x-reqid` 传入请求唯一编号；登录后使用 `authorization: Bearer <token>` 表达登录态，使用 `x-udid` 表达设备或用户唯一标识，受保护接口同时要求 `x-timestamp`、`x-sign` 防篡改签名、`x-sign-alg` 签名算法和 `x-api-version` 契约版本，并执行防重放、权限检查、输入校验和审计日志；登录、验证码、探活等公开接口不需要 token 或签名认证，也不具备 `x-udid`，必须配置 `auth-exclude-paths` 跳过整条认证链。
   - 公开客户端 API：前端或客户端必须通过 `x-reqid` 传入请求唯一编号；登录态仍主要放在 `authorization`，客户端身份使用 `x-api-key`，`x-timestamp` 校验时间窗口，使用 `x-api-key + x-reqid` 作为防重放键，不再使用 `x-nonce`，签名结果统一使用 `x-sign`，签名算法使用 `x-sign-alg`，契约版本使用 `x-api-version`，原始 body 字节参与签名，配合重放缓存和限流。
   - 交易 API：公开客户端 API 要求，加业务唯一键、状态机、唯一约束、对账和不可变审计记录。

3. 在设计实现或评审代码前固定实现决策。
   - 阅读 `references/implementation-standard.md`。
   - 公司级生产标准同时阅读 `references/production-stack.md`。
   - 涉及日志、指标、链路追踪或生产告警时阅读 `references/observability-standard.md`。
   - 决定 JDK 版本、Spring Boot 代际、校验包、持久化栈、HTTP 状态与业务结果策略、错误码风格、JSON/时间约定和空数据行为。
   - 涉及 Spring Boot、Spring Cloud、Nacos、MyBatis-Plus 等版本选择时阅读 `references/version-compatibility.md`，优先采用公司验证过的版本矩阵。

4. 确认分层和模块规则归属。
   - 阅读 `references/layering.md` 获取 API 标准与分层职责的边界摘要；类/方法职责、事务、异常、日志和测试细节使用 `java-development-principles`。
   - 多模块项目阅读 `references/module-standard.md` 获取 API 标准与模块设计的边界摘要；Maven 模块、父子 POM、`common` 边界和依赖方向使用 `java-multi-module-architecture`。
   - 涉及数据库、幂等、审计或交易时阅读 `references/database-standard.md`。
   - 设计、实现或评审普通后台 CRUD 时阅读 `references/crud-standard.md`。
   - Controller 不得包含业务规则或数据库访问。
   - DTO 不得复用为持久化实体。

5. 应用 API 契约。
   - 阅读 `references/api-contract.md`。
   - 涉及接口版本变更、错误码冻结或弃用策略时阅读 `references/api-lifecycle-standard.md`。
   - 每个 HTTP API 都必须使用统一响应包装、统一错误码模型、一致分页、参数校验和追踪字段。

6. 应用安全与可靠性规则。
   - 阅读 `references/security.md`。
   - 涉及 CMS 后台权限、角色、菜单或数据权限时阅读 `references/authz-standard.md`。
   - 如涉及 TCP/UDP/WebSocket，本技能只定义与 Java API 标准共享的响应、错误码、安全和日志摘要；完整协议 envelope、ACK、心跳、连接治理和 handler dispatcher 规则必须使用 `netty-handler-dispatcher`。
   - 涉及文件上传、对象存储、远程调用或跨系统事务时阅读 `references/file-upload-standard.md` 和 `references/resilience-standard.md`。
   - 判断当前 API 类别是否必须启用防重放、防篡改和幂等。

7. 需要生成完整项目或基础代码时切换到生成器。
   - 本技能只定义规则限制和检查标准，不携带 Java 代码资产。
   - 需要创建 Java 后端脚手架、基础设施代码或 CRUD 样例时，使用 `java-backend-project-generator`；`minimal` profile 生成 `common/cms-api`，`standard` profile 生成 `common/cms-api/sdk-api`。
   - 本技能可在生成后运行检查器验证生成结果是否符合规则。

8. 使用清单和可选静态检查验证。
   - 阅读 `references/checklists.md`。
   - 修改或解释静态检查覆盖范围时阅读 `references/checker-coverage-matrix.md`。
   - 评审或验证生成项目时运行 `scripts/check_java_api_standard.py <project-root> --profile minimal|standard --fail-on-error`；需要机器读取时追加 `--json`。
   - 修改检查器规则后运行 `scripts/test_check_java_api_standard.py`，确认废弃请求头、minimal 残留、生成器 base-template 和 profile 参数拒绝规则没有回退。
   - 修改本技能文档或资源结构后运行 `scripts/check_java_backend_api_standard_skill.py`，确认技能自身目录、引用、长文档目录和异常边界口径没有漂移。
   - 完成评审、重构或生成结果检查前，报告哪些清单项通过、失败或需要用户确认。
   - 使用静态检查器时，最终回复必须同时报告人工检查边界：权限模型语义、业务幂等语义、生产替换落地、真实 SQL 执行计划和未运行的集成测试，不得把 checker 通过描述为项目已经生产可用。

## 内置资源

- `references/implementation-standard.md`：固定实现决策，避免项目之间漂移。
- `references/api-contract.md`：请求/响应、分页、错误码、参数校验和 OpenAPI 契约规则。
- `references/api-lifecycle-standard.md`：API 版本、废弃、兼容性、错误码冻结和契约测试治理规则。
- `references/layering.md`：API 标准与分层职责的交界摘要；详细类/方法职责、事务、异常、日志和测试规则使用 `java-development-principles`。
- `references/module-standard.md`：API 标准与模块设计的交界摘要；详细 Maven 模块、`common` 边界和依赖方向使用 `java-multi-module-architecture`。
- `references/security.md`：认证鉴权、防重放、防篡改、原始 body 签名、幂等、审计、CORS 跨域和 SQL 注入防护要求。
- `references/production-stack.md`：公司级生产技术栈、配置中心、Redis、网关、监控和对象存储选择规则。
- `references/observability-standard.md`：访问日志、JSON 日志、指标、链路追踪、告警和生产端点暴露标准。
- `references/version-compatibility.md`：Spring Boot、Spring Cloud、Nacos、MyBatis-Plus、JDK 和 OpenAPI 版本兼容矩阵。
- `references/database-standard.md`：数据库迁移、表字段、操作审计表、幂等表、唯一约束和 SQL 安全规则。
- `references/crud-standard.md`：普通后台 CRUD 的 controller、DTO、service、mapper、entity、converter、迁移脚本和测试生成规则。
- `references/authz-standard.md`：CMS 鉴权、权限码、角色、菜单、数据权限、多租户和审计规则。
- `references/netty-transport-standard.md`：Netty TCP/UDP/WebSocket 在 Java API 标准侧的摘要边界；完整协议、签名、ACK、心跳和 handler dispatcher 规则使用 `netty-handler-dispatcher`。
- `references/file-upload-standard.md`：文件上传、对象存储、预签名 URL、魔数校验和生产扫描标准。
- `references/resilience-standard.md`：超时、重试、熔断、隔离、outbox 和远程调用事务边界标准。
- `references/checklists.md`：新项目、API 评审和高风险交易验收检查清单。
- `references/api-standard-contract.json`：profile、通用请求头、SDK 请求头、废弃请求头和签名头常量片段的共享契约。
- `references/checker-coverage-matrix.md`：静态检查器规则 ID、覆盖范围和人工检查边界。
- `references/production-replacement.md`：生产环境必须替换的内存实现、固定密钥、日志审计、幂等、限流和权限模型清单。
- `references/forward-test-scenarios.md`：维护本技能后用于前向验证的样例任务和预期关注点，普通 API 任务不必默认读取。
- `scripts/check_java_api_standard.py`：用于发现明显 API 标准违规的静态项目检查器。
- `scripts/check_java_backend_api_standard_skill.py`：用于检查本技能自身结构、引用文件、长 reference 目录、残留构建产物和关键规则口径。
- `scripts/run_forward_tests.py`：用于列出并检查 forward-test 场景结构；追加 `--prompts` 可输出可复制给人工或子任务执行的测试 prompt；维护技能后运行，不能替代人工或子任务真实验证。

## 必需输出格式

用于定义新 Java 项目的 API 标准时，应返回：

- 项目分类和假设。
- 推荐包结构或模块结构。
- 必须的 API 请求头和 body 规则。
- 统一响应格式。
- 错误码约定。
- 正常业务失败与程序异常边界：业务失败返回稳定错误码，不作为异常控制流，不打印 `error` 堆栈；真正异常不得吞掉，必须脱敏记录。
- DTO/request/response 命名规则。
- 参数校验和 i18n message 规则。
- 安全档位：认证、签名、防重放、防篡改、幂等。
   - 如涉及 TCP/UDP/WebSocket，本技能只定义与 Java API 标准共享的响应、错误码、安全和日志摘要；完整协议 envelope、ACK、心跳、连接治理和 handler dispatcher 规则必须使用 `netty-handler-dispatcher`。
- 浏览器跨域和 SQL 注入防护要求。
- 日志和审计要求。
- 最小测试和验收清单。

用于重构或检查生成结果时，应实现能让项目符合标准的最小范围改动，然后在可用时运行相关构建或测试。需要从零生成项目时，使用 `java-backend-project-generator`。

当其他 Java 技能也相关时，应有意组合使用：

- 使用 `java-multi-module-architecture` 处理 Maven 父子模块、依赖方向和模块边界。
- 使用 `java-microservice-dev` 实现具体 Spring Boot 业务功能。
- 使用 `java-code-review` 对现有 Java 代码库做风险导向评审。
- 使用 `java-development-principles` 应用通用可维护性和编码规则。

## 设计原则

- 先标准化外部可见契约，再把实现细节放在 service 后面。
- 除非领域足够复杂需要更丰富的领域建模，否则优先采用简单 Spring Boot 分层。
- 区分后台管理 API 与公开/移动端/开放 API。不要把后台脚手架原样复制到高并发或高安全系统。
- 不要随意手写安全机制。先使用框架认证鉴权，再在需要的边界增加 `x-timestamp` 时间窗口校验、`x-sign` 防篡改签名、按调用方拆分的 replay key 防重放和业务幂等；`authorization` 主要承载登录后的 token，不承载签名结果。
- 保持响应格式统一，同时通过泛型让业务数据保持强类型。
- 区分正常业务失败和程序异常。未登录、无权限、参数错误、客户端协议格式错误、资源不存在、状态不允许、幂等冲突、签名失败和重放请求等可预期结果应返回稳定错误码并进入访问日志/metrics；不要通过抛异常和 `log.error` 堆栈表达。真正被捕获并消费的程序异常、依赖异常、协议解析器缺陷、ACK/响应写出失败和审计失败必须 `log.error` 脱敏记录，不得吞掉。
- 源码使用 UTF-8。面向用户的校验消息优先使用 i18n message code，使 API 契约跨语言和客户端保持稳定。
