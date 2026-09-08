# Java Skills

本项目集中存放 Java/Netty 后端相关 Codex skills，用于规范 AI 辅助开发、代码审查、项目脚手架、生产事故处理、Netty 协议设计和项目知识库沉淀。

核心目标：

- 让 AI 编码先进入标准框架，再做业务实现。
- 避免 AI 自由发挥导致接口、日志、鉴权、模块边界和异常处理不一致。
- 将重复规则收敛到权威 skill，其他 skill 只做摘要和引用。
- 让架构设计、编码、审查和故障处理使用同一套后端规范。

## 项目定位

这不是普通 Java 业务工程，而是一组面向 Codex 的 Java 后端开发规范与操作手册。它适用于以下场景：

- 新建 Java/Spring Boot 后端项目。
- 在已有 Java 项目中开发接口、业务逻辑、MQ、Redis、外部调用和测试。
- 设计 Maven 多模块架构和模块边界。
- 统一 HTTP/API 响应、错误码、请求头、签名、防重放和幂等规则。
- 设计或审查 Netty TCP、UDP、WebSocket 协议入口。
- 做 Java 代码审查和生产事故修复。
- 为项目生成 `AGENTS.md` 和 `docs/vibecoding` AI 编程知识库。

## 核心关系

```text
java-backend-development-orchestrator
        |
        +-- java-backend-api-standard
        +-- java-backend-project-generator
        +-- java-microservice-dev
        +-- java-multi-module-architecture
        +-- java-development-principles
        +-- java-code-review
        +-- java-incident-fix
        +-- netty-handler-dispatcher
        `-- vibecoding-knowledge-base
```

`java-backend-development-orchestrator` 是统一入口；其他 skill 是专项权威。使用时先判断任务类型，再加载最小必要 skill 集合。

## 目录结构

```text
java-skills/
|-- README.md
`-- skills/
    |-- java-backend-development-orchestrator
    |-- java-backend-api-standard
    |-- java-backend-project-generator
    |-- java-microservice-dev
    |-- java-multi-module-architecture
    |-- java-development-principles
    |-- java-code-review
    |-- java-incident-fix
    |-- netty-handler-dispatcher
    `-- vibecoding-knowledge-base
```

## Skill 职责

| Skill | 主要职责 |
| --- | --- |
| `java-backend-development-orchestrator` | Java/Netty 后端统一入口，负责选择主责 skill、辅助 skill 和执行顺序。 |
| `java-backend-api-standard` | HTTP/API 契约、统一响应、错误码、`reqid`、请求头、鉴权、签名、防重放、幂等和 OpenAPI 标准。 |
| `java-backend-project-generator` | 从零生成 Java/Spring Boot Maven 后端脚手架，支持 `minimal`、`standard` 和显式 Netty 模块。 |
| `java-microservice-dev` | 在已有 Spring Boot 项目中实现具体 Controller、Service、Mapper/JPA、Feign、MQ、Redis、配置和测试。 |
| `java-multi-module-architecture` | Maven 多模块、父子 POM、模块边界、依赖方向、`common` 边界和模块级 `AGENTS.md`。 |
| `java-development-principles` | SOLID、职责拆分、分层依赖、事务、异常、日志、测试、类/方法大小和组合复用。 |
| `java-code-review` | Java/Spring Boot PR、diff、commit 或已有代码变更的风险导向审查。 |
| `java-incident-fix` | Java/Spring Boot 生产事故、线上故障、数据风险、安全事件的止血、定位、恢复和 RCA。 |
| `netty-handler-dispatcher` | Netty TCP/UDP/WebSocket 协议入口、`func + version`、handler dispatcher、ACK、心跳和连接治理。 |
| `vibecoding-knowledge-base` | 生成或更新根/模块级 `AGENTS.md`、`docs/vibecoding`、系统边界、证据链和 AI 编程知识库。 |

## 在 Codex 中使用

1. 将本项目的 `skills/` 下各 skill 目录复制到本机 Codex skills 目录：

```text
D:\Users\CodexData\.codex\skills
```

推荐复制完整 `skills/` 目录，避免 `java-backend-development-orchestrator` 无法路由到专项 skill。

2. 在 Codex 新建或打开一个 Java 后端任务。复杂任务优先显式指定统一入口：

```text
使用 $java-backend-development-orchestrator 帮我判断这个 Java 后端需求应该走哪个开发流程。
```

3. 单一专项任务可以直接指定权威 skill。下面的提示词可直接复用：

```text
使用 $java-backend-api-standard 帮我检查这个接口是否符合统一响应、错误码和请求头标准。
```

```text
使用 $java-backend-project-generator 为 Spring Boot 2 / JDK 8 项目生成 Maven 多模块脚手架。
```

```text
使用 $java-code-review 审查当前变更，按严重程度列出缺陷、风险和缺失测试。
```

```text
使用 $netty-handler-dispatcher 设计 UDP 协议入口和 handler 分发，统一响应模型与 ACK 策略。
```

4. 即使不显式写 `$skill`，在任务描述中清楚说明 Java、Spring Boot、接口标准、Netty、代码审查或线上故障等关键词时，Codex 也可按 skill 的适用范围选择相应规则。涉及多个专项、需要编排执行顺序时，仍建议显式指定 `java-backend-development-orchestrator`，结果更稳定、更容易追溯。

## 推荐使用方式

新项目：

```text
java-backend-development-orchestrator
-> java-backend-project-generator
-> java-backend-api-standard
-> java-multi-module-architecture
-> java-development-principles
-> java-microservice-dev
```

已有项目开发：

```text
java-backend-development-orchestrator
-> java-multi-module-architecture
-> java-backend-api-standard
-> java-microservice-dev
-> java-development-principles
```

代码审查：

```text
java-code-review
+ java-backend-api-standard / java-development-principles / java-multi-module-architecture / netty-handler-dispatcher 按需辅助
```

生产事故：

```text
java-incident-fix
-> java-microservice-dev
-> java-code-review
```

知识库沉淀：

```text
vibecoding-knowledge-base
+ java-multi-module-architecture / java-backend-api-standard / netty-handler-dispatcher 按需辅助
```

## 使用效果

| 使用场景 | Codex 获得的约束与产出 | 预期效果 |
| --- | --- | --- |
| 新建后端项目 | 先确定模块边界、脚手架 profile、API 契约和基础治理项。 | 避免只生成业务代码而遗漏统一返回、异常、日志、鉴权和测试基础设施。 |
| 开发接口或业务功能 | 按 Controller、Service、数据访问、外部调用和测试的职责实现，并复用统一错误码与 `reqid` 规则。 | 减少接口风格漂移，便于联调、排障和后续扩展。 |
| 多模块演进 | 明确父子 POM、依赖方向、`common` 边界和模块级知识。 | 降低模块互相依赖、公共包膨胀和“改一处牵全身”的风险。 |
| Netty 协议开发 | 统一协议入口、分发键、响应报文、ACK、心跳与连接治理。 | 让 TCP、UDP、WebSocket 不再各自定义一套处理方式。 |
| 代码审查与事故修复 | 以缺陷风险、兼容性、数据一致性和恢复步骤为中心输出结论。 | 更早暴露线上风险，并形成可验证的修复与复盘依据。 |
| 项目知识沉淀 | 生成根和模块级 `AGENTS.md`、架构边界和证据链。 | 让后续 Codex 任务理解项目约束，减少每次从零解释背景。 |

## 维护原则

- `java-backend-development-orchestrator` 只做导航，不重复承载专项详细规则。
- 共享规则只保留在一个权威 skill 中，其他 skill 通过摘要和引用使用。
- 修改 skill 后必须运行对应 `scripts/check_*_skill.py`。
- 维护 forward-test 场景后必须运行对应 `scripts/run_forward_tests.py`。
- 不要保留同一内容的中英文双轨副本，避免规则漂移。

## 公开发布说明

- `java-backend-project-generator` 中包含脚手架模板和开发占位配置，例如示例账号、示例 token、示例 apiKey、示例 secret。
- 这些值仅用于本地开发和模板演示，不得作为生产凭证使用。
- 基于本项目生成真实业务系统后，必须替换所有开发占位密钥、内存实现、默认账号和示例配置。
