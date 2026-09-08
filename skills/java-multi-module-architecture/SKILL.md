---
name: java-multi-module-architecture
description: Use when 需要设计、创建、拆分、重构或文档化 Java Maven/Spring Boot 多模块项目，处理父工程、子模块、POM、模块边界、依赖方向、AGENTS.md、架构文档、脚手架脚本或多模块验证。
---

# Java 多模块项目架构

本技能用于把 Java/Spring Boot 后端项目设计成职责清晰、依赖方向明确、可构建、可测试、便于 AI 维护的多模块结构。

本技能是 Maven 多模块、POM、模块职责、依赖方向、`common` 边界和模块级 `AGENTS.md` 的权威来源。类/方法职责、SOLID、事务、异常、日志和测试由 `java-development-principles` 负责；HTTP/API 契约由 `java-backend-api-standard` 负责；具体业务实现由 `java-microservice-dev` 负责。

优先遵循目标仓库已有约定。如果项目已有 `AGENTS.md`、父 POM、模块文档、脚手架或构建规范，先读取并遵守现有规则。

## 何时使用

当用户要求以下任务时使用本技能：

- 创建 Java Maven/Spring Boot 多模块项目。
- 将单模块 Java 项目拆分为多模块。
- 设计多模块架构、模块职责、依赖方向或部署边界。
- 生成或修订多模块 POM、AGENTS.md、模块地图和架构文档。
- 检查多模块项目的依赖方向、模块边界、构建和测试方式。

如果用户明确使用 Gradle，不要强行生成 Maven；先说明本技能默认 Maven，并按 Gradle 项目已有约定调整。用户未说明构建工具时，默认 Maven。

## 执行模式

先判断用户目标，只选择能满足目标的最小模式：

| 模式 | 使用场景 | 允许输出 | 禁止动作 |
| --- | --- | --- | --- |
| `analysis-only` | 只分析当前项目 | 模块职责、依赖方向、风险和建议 | 修改文件 |
| `architecture-design` | 设计新系统或新结构 | 模块方案、依赖图、目录规划 | 生成业务代码 |
| `scaffold-new-project` | 创建新多模块项目 | 父 POM、子 POM、目录、最小启动类、AGENTS.md | 生成未确认业务实现 |
| `refactor-existing-project` | 拆分或重构已有项目 | 迁移计划、分阶段改动、验证命令 | 一次性大搬迁 |
| `docs-only` | 只补文档或 AGENTS.md | 根和模块 AGENTS.md、架构文档 | 修改业务代码和运行配置 |
| `pom-only` | 只修 Maven 多模块构建 | POM 调整、构建说明、验证结果 | 顺手重构源码 |

## 默认技术假设

新项目默认：

- Maven 多模块。
- Java 17 或 21。
- Spring Boot 4.x。
- JUnit 5。
- UTF-8 编码。

老项目默认：

- 保持现有 Java、Spring Boot、Spring Cloud、依赖版本和包名兼容。
- 不主动升级 Spring Boot 主版本或迁移 `javax.*` / `jakarta.*` 技术线。
- 不改变 API、MQ、协议和数据库兼容行为，除非用户明确要求。

## 最小执行路径

### 创建新项目

1. 确认 `projectName`、`groupId`、`basePackage`、`javaVersion`、`springBootVersion`、模块清单。
2. 判断是否可以使用目标仓库已有模板；没有模板时可使用 `scripts/scaffold-maven-multimodule.ps1` 或 `.sh`。
3. 生成父 POM 和子模块 POM。
4. 生成最小目录结构，只给可部署模块创建启动类。
5. 生成根 `AGENTS.md` 和模块级 `AGENTS.md`。
6. 运行 `mvn -q -DskipTests compile` 或说明无法运行原因。

### 分析或文档化已有项目

1. 读取根 POM、子 POM、模块目录、启动类、配置、测试和已有文档。
2. 识别 HTTP、MQ、定时任务、协议服务、外部系统、数据库、Redis、对象存储等入口和依赖。
3. 输出模块职责、上下游、可部署模块、库模块、依赖方向和风险。
4. 如果要求生成文档，优先使用 `templates/` 下的模板。

### 拆分已有项目

1. 先输出阶段化迁移计划，不直接大搬迁。
2. 优先抽取稳定契约到 `common` 或 contract/client 模块。
3. 再拆入口模块、异步模块、外部系统适配模块。
4. 每个阶段都必须能独立构建、测试和回滚。

## 模块边界原则

- 一个模块只承担一种主要职责。
- `common` 只放稳定共享契约、常量、错误码、配置属性、纯工具。
- 不要把 controller、service 实现、mapper、MQ consumer、外部系统实现放入 `common`。
- 可部署模块之间默认禁止 Maven 互相依赖；如确需依赖，必须说明原因，并优先抽取 contract/client/common 模块。
- HTTP API、MQ 消息体、自定义协议报文、外部系统 DTO 不要互相污染。
- 只有存在独立启动类、端口、配置、消费者、定时任务或部署产物时，才视为可部署模块。
- 新增模块前必须说明职责、上游、下游、拥有入口、拥有状态、禁止放入内容。

当模块设计涉及 TCP/UDP/WebSocket 或 Netty 长连接入口时，本技能只判断模块职责、依赖方向和可部署边界；协议 envelope、handler dispatcher、ACK、心跳和连接治理由 `netty-handler-dispatcher` 负责。

详细模块规则见 `references/module-boundary-rules.md`。

## 模块内部目录基线

每个模块内部应按职责分包，避免把 controller、service、repository、DTO、config、utils 等混放在同一目录。

常见目录职责：

| 目录 | 职责 |
| --- | --- |
| `controller` | HTTP 接口入口 |
| `service` | 业务编排和应用服务 |
| `domain` / `model` | 领域对象或内部模型 |
| `dto` / `request` / `response` / `vo` | 接口传输对象 |
| `repository` / `mapper` / `dao` | 数据访问 |
| `client` / `feign` / `adapter` | 外部系统调用 |
| `listener` / `consumer` | MQ 消费入口 |
| `producer` | MQ 生产 |
| `config` | Spring 配置和属性绑定 |
| `constants` / `enums` | 稳定常量和枚举 |
| `exception` | 异常定义和异常映射 |
| `validation` | 参数校验或业务校验 |
| `handler` / `strategy` | 策略、处理器、扩展点 |
| `utils` | 纯工具类，不允许放业务流程 |

本技能只约束模块内部的目录职责边界。类、方法、DTO/VO/Entity、异常、日志、测试等详细编码规范由 `java-development-principles` 承接。

## Maven 基线

- 根 `pom.xml` 使用 `<packaging>pom</packaging>`。
- 所有启用模块放入 `<modules>`。
- 版本集中在 `<properties>`、`<dependencyManagement>` 和 `<pluginManagement>`。
- 子模块继承父工程。
- 只有可部署 Spring Boot 模块使用 `spring-boot-maven-plugin`。
- 库模块默认不生成可执行 jar。
- 新项目建议包含 Maven Wrapper、`.editorconfig`、`.gitattributes` 和 UTF-8 编码配置。

模板见：

- `templates/parent-pom.xml`
- `templates/child-pom.xml`

## 脚手架规则

用户明确要求“创建项目”“生成脚手架”“初始化多模块工程”时，可以使用：

- Windows: `scripts/scaffold-maven-multimodule.ps1`
- Linux/macOS: `scripts/scaffold-maven-multimodule.sh`

脚手架只生成最小可编译结构，不生成登录、权限、用户表、数据库 schema、MQ topic、Docker、Kubernetes、CI/CD 或示例业务逻辑，除非用户明确要求。

脚手架不得覆盖已有文件，除非用户明确允许。

## 验证规则

能运行 Maven 时优先执行：

```bash
mvn -q -DskipTests compile
mvn test -pl <module> -DskipTests=false
mvn clean package -pl <module> -am -DskipTests
```

多模块结构检查可使用：

- Windows: `scripts/validate-maven-modules.ps1`

修改本技能、模板或引用文件后运行：

```powershell
py "D:\Users\CodexData\.codex\skills\java-multi-module-architecture\scripts\check_java_multi_module_architecture_skill.py"
```

维护模块边界规则后运行 `scripts/run_forward_tests.py`；场景定义在 `references/forward-test-scenarios.md`，追加 `--prompts` 可输出可复制给人工或子任务执行的场景 prompt。

如果内部依赖、Nacos、Redis、MQ、数据库或私服不可用，说明阻塞原因，并尽量完成静态结构验证。

## 文档输出

创建或调整多模块结构时，优先生成：

- 根 `AGENTS.md`
- 每个模块的 `AGENTS.md`
- `docs/architecture/module_map.md`
- `docs/architecture/system_architecture.md`
- `docs/development/module_development_guide.md`

模板见 `templates/`。

## 与其他 Java 技能协同

- 设计模块结构时先用本技能。
- 前后端分离 HTTP API 标准使用 `java-backend-api-standard`。
- 实现具体接口或业务逻辑时，再使用 `java-microservice-dev`。
- 约束类、方法、controller/service/repository/DTO 职责时，配合 `java-development-principles`。
- 审查代码风险时，配合 `java-code-review`。
- 生产故障处理时，优先使用 `java-incident-fix`。

## 验收标准

完成前检查：

- 当前执行模式明确，且没有做模式禁止的动作。
- 父工程、启用模块、未启用模块已经区分。
- 每个模块职责能用一句话说明。
- 依赖方向清晰，没有新增循环依赖。
- `common` 没有包含易变业务实现或运行时入口。
- 可部署模块有启动边界和启动说明。
- 文档能指导后续开发者定位应该修改哪个模块。
- 已运行可行的 Maven 验证命令，或说明无法运行原因。
- 如果创建脚手架，确认没有生成未要求的业务逻辑、数据库表、MQ topic 或运行时配置。

## 输出要求

最终回复说明：

- 新增或修改的文件。
- 最终模块结构。
- 依赖方向。
- 可部署模块。
- 已运行的构建和测试命令。
- 已知缺口、假设或未验证原因。
