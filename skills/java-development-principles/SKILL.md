---
name: java-development-principles
description: Use when Java/Spring Boot 任务需要判断职责拆分、SOLID、分层依赖、事务、异常、日志、测试、类/方法大小、组合复用，或避免 controller/service/repository/DTO/entity 混杂；HTTP/API 契约细节使用 java-backend-api-standard。
---

# Java 开发原则

使用本技能保持 Java 后端改动小而聚焦、分层清晰、可测试且易扩展。优先遵循项目既有约定；当代码库没有清晰模式时，执行以下原则。

## 核心规则

- 一个类和文件只承担一个主要职责。
- 保持 Controller 轻薄，将业务流程放入 Service。
- 将数据访问限定在 repository、mapper、DAO 或 gateway 中。
- DTO、entity、VO、command 和响应对象保持分离，除非项目已有有意为之的简化模式。
- 优先通过接口、策略、handler、factory、registry 或配置扩展，而非反复修改中心分支逻辑。
- 避免推测性抽象；只有能消除真实重复或保护真实扩展点时才新增抽象。
- 除非用户明确要求破坏性变更，否则保持 API 兼容性。
- 为改动的行为新增或更新测试。
- 优先遵循项目既有的 Java 版本、Spring Boot 版本、包结构、响应模型、错误码模型和测试风格；不要仅因本技能给出基线就引入竞争性约定。

## 版本兼容

新增导入、注解、依赖或测试前，先识别项目版本线：

| 项目版本 | 校验导入 | 基线说明 |
| --- | --- | --- |
| Spring Boot 2.x | `javax.validation.*` | 项目要求时保持 Java 8/11 兼容性。 |
| Spring Boot 3.x | `jakarta.validation.*` | 需要 Java 17+；除非项目已有兼容桥接，否则不要使用旧 `javax.*` API。 |
| Spring Boot 4.x | `jakarta.validation.*` | 需要 Java 17+ 并采用 Spring Framework 7 / Jakarta 路线；除非用户要求大版本升级，否则保持 Boot 3.x 项目不变。 |
| JUnit 4 项目 | `org.junit.*` | 不要静默迁移测试至 JUnit 5。 |
| JUnit 5 项目 | `org.junit.jupiter.*` | 使用 Jupiter 模式和既有扩展。 |

无法确认版本时，编辑前检查 `pom.xml`、Gradle 文件、导入和既有测试。

## 包结构基线

优先使用项目现有布局。没有清晰本地约定时，按职责分离包结构：

| 包 | 职责 |
| --- | --- |
| `controller` | 仅承载 HTTP 入口。 |
| `service` / `service.impl` | 业务编排和应用用例。 |
| `domain` / `model` | 领域对象或内部模型。 |
| `entity` | 持久化实体。 |
| `dto` / `request` / `response` / `vo` | API 契约和传输对象。 |
| `repository` / `mapper` / `dao` | 数据访问。 |
| `client` / `feign` / `adapter` / `gateway` | 外部系统调用。 |
| `listener` / `consumer` / `producer` | MQ 消费/生产边界。 |
| `config` | Spring 配置和属性。 |
| `exception` | 异常、错误码和异常映射。 |
| `validation` | 请求或业务校验。 |
| `handler` / `strategy` / `factory` | 扩展点和业务变体。 |
| `utils` | 仅放纯无状态工具，绝不放置业务流程。 |

## 分层职责

### 控制器

- 接收请求、校验 DTO、调用应用或 Service 层并返回响应。
- 不包含业务规则、SQL、远程 API 编排、重事务逻辑或复杂分支。
- 可用时使用 JSR-380 校验请求 DTO。

### 服务 / 用例

- 承担业务工作流、事务边界、带权限意识的业务决策和编排。
- 保持 public 方法意图命名清晰。
- 大型工作流仅在能提高可读性时拆为私有方法，或在职责分化时拆为协作者。

### 仓储 / Mapper / DAO

- 仅承担持久化操作。
- 除非现有架构要求，否则不要从持久化代码返回传输 DTO。
- 避免 N+1 查询、无界集合加载和隐式懒加载带来的意外。

### 领域 / 实体

- 表达领域状态和领域行为。
- 不依赖 Web、持久化框架细节或请求/响应对象。

### DTO / 请求 / 响应

- 表达 API 输入和输出契约。
- 除校验注解和项目既有的简单派生格式化外，不要将业务规则放入 DTO。

## API 传输规则

HTTP/HTTPS `POST` 和后端 WebSocket 消息默认使用 JSON；二进制、protobuf、SSE、文件上传下载、第三方回调等是例外。Netty TCP/UDP/WebSocket envelope、ACK、心跳、连接治理和签名 canonicalization 由 `netty-handler-dispatcher` 负责。

- 本地框架或约定未声明时，显式设置媒体类型，例如 `Content-Type: application/json` 和 `Accept: application/json`。
- HTTP/HTTPS 请求/响应体和 WebSocket 消息应定义明确 DTO；除非既有项目约定有意要求，否则不要在 API 边界传递原始 `Map`、持久化实体或内部领域对象。
- 在 controller、client 或协议适配器边界记录非 JSON 传输格式，并说明 JSON 不适用的原因。

## HTTP 响应模型边界

HTTP/API 统一响应、错误码、`reqid`、`status` 是否冗余、`traceId` 是否公开返回等详细规则，以 `java-backend-api-standard` 为权威来源。

本技能只保留编码侧约束：

- Controller 必须返回项目既有统一响应模型，不要自定义第二套响应包装。
- 不要在 controller、service 或 exception handler 中散落硬编码错误码。
- 不要新增与权威响应模型冲突的 `status`、`traceId` 或重复成功标识。
- 如果项目已有历史响应模型，先保持兼容；需要迁移时由 `java-backend-api-standard` 设计契约。

## SOLID 指导

核心判断：

- 单一职责：一个类或文件只承担一个主要职责；混合请求解析、授权、业务规则、持久化、远程调用、响应格式化、事件发布中的多项时应拆分。
- 开放封闭：新增业务类型、渠道、策略、供应商或规则时，优先通过接口、handler、策略、factory、registry 或配置扩展。
- 依赖倒置：service 依赖端口或接口，基础设施实现隐藏在 client、gateway、repository 或 adapter 后。
- 接口隔离：接口聚焦一个调用方需要或一个内聚能力，避免过大的 manager 接口。
- 组合复用：优先组合小型 service、策略、校验器、handler 和 adapter，不用大型抽象基类承载可变业务流程。

详细拆分信号、反例和处理方式见 `references/detailed-principles.md`。

## 事务、异常与日志

- `@Transactional` 放在 service/use-case 层，不放在 controller；事务范围尽可能小，避免在事务中包住慢远程调用。
- 捕获异常只用于补充上下文、有意恢复或转换边界错误；不得吞异常或多层重复打印同一堆栈。
- 请求摘要日志应包含 trace id、方法、路径、状态和耗时；敏感字段必须脱敏。

详细规则和常见反模式见 `references/detailed-principles.md`。

## 文件大小与拆分信号

向现有文件添加代码前，检查改动是否令文件承担第二项职责。

出现以下信号时拆分或引入协作者：

- controller 开始包含业务规则。
- service 开始处理持久化细节和外部 API 协议细节。
- 一个类约超过 600 行，且新增改动扩展了不同职责。
- 一个方法约超过 100 行，且混合校验、分支、持久化和响应映射。
- 重复的 `if/else` 或 `switch` 块处理业务变体。
- 新代码必须启动整个应用才能进行单元测试。

这些阈值是信号，不是机械规则；存在更严格的项目本地约定时应遵循该约定。

## 实现前检查清单

编辑前：

- 确认改动所属层次。
- 确认要新增或修改的文件以及每个文件的职责。
- 检查已有模式和扩展点。
- 定义改动的验证方式。
- 确认是否需要 `java-multi-module-architecture` 决定模块放置位置。
- 确认是否需要 `java-microservice-dev` 提供具体 Spring Boot 实现模式。

编辑期间：

- 将改动限定在请求的行为内。
- 匹配项目既有的命名、包结构、错误处理和测试风格。
- 优先新增聚焦文件，而不是扩大职责混杂的文件。
- 不做无关重构。

完成前：

- 运行与变更模块相关的编译或测试。
- 检查 API 兼容性和错误行为。
- 检查事务边界。
- 检查日志是否泄露敏感数据。
- 说明所有未经验证的风险。

## 审查与测试摘要

审查 Java 改动时重点检查：controller 业务逻辑、service 持久化细节、DTO/entity 跨层泄露、事务边界、吞异常、错误码不一致、敏感日志和缺少测试。

测试选择遵循最小可验证原则：controller 用项目既有 Web 测试风格；service 用单元测试或项目认可替身；mapper/repository 用数据访问测试；外部 client、MQ、事务和幂等覆盖代表性边界。详细表格见 `references/detailed-principles.md`。

## Skill 边界

- 使用 `java-multi-module-architecture` 处理父工程、模块边界、依赖方向、POM 结构和模块级 AGENTS.md。
- 本技能处理类/文件职责、分层、SOLID、事务、异常、日志和测试。
- 使用 `java-microservice-dev` 处理具体的 Spring Boot API、service、数据访问、校验、配置和测试实现。
- 除非用户明确要求重构，且架构 skill 已确定模块边界，否则不要用本技能执行广泛模块重组。

## 详细引用

- `references/detailed-principles.md`：SOLID 细则、事务、异常、日志、常见反模式、审查清单和测试策略。

## 可选静态检查

审查或重构 Java 代码时，下列辅助脚本可提供快速证据。它们仅作建议，不能替代代码阅读：

- `scripts/check-large-files.ps1`：标记大型 Java 文件和长方法。
- `scripts/check-java-layering.ps1`：标记常见分层风险，例如 controller `@Transactional` 或 controller 导入 mapper/repository。
- `scripts/check-sensitive-logging.ps1`：标记提及敏感字段的日志语句。

从项目根目录运行这些脚本，并在变更前人工审查发现项。

修改本技能后运行：

```powershell
py "D:\Users\CodexData\.codex\skills\java-development-principles\scripts\check_java_development_principles_skill.py"
py "D:\Users\CodexData\.codex\skills\java-development-principles\scripts\run_forward_tests.py"
```

前向验证场景位于 `references/forward-test-scenarios.md`；维护本技能后可用 `scripts/run_forward_tests.py --prompts` 输出场景 prompt，用 `--score-output`、`--score-dir` 或 `--score-fixtures` 对真实输出做 keyword scoring。

## 输出期望

使用本技能实施时，汇总：

1. 修改文件及其职责。
2. 选定层或模块适当的原因。
3. 已运行的验证命令。
4. 剩余风险或后续事项。
