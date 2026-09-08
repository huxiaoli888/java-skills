---
name: java-backend-development-orchestrator
description: Use when Java/Netty 后端任务范围不止一个专项，或需要在 API 标准、脚手架、多模块、开发原则、微服务实现、代码审查、事故修复、Netty TCP/UDP/WebSocket 协议入口、AGENTS.md 或 docs/vibecoding 知识库之间选择正确入口。
---

# Java/Netty 后端开发统一入口

本技能是 Java/Netty 后端工作的统一入口。它不承载详细规则，不替代专项技能；它只负责判断任务类型、选择权威 skill、确定执行顺序和边界。

## 核心原则

- 优先使用最小 skill 集合，不要默认加载所有 Java/Netty skill。
- 先用本技能判断“谁是主责”，再按需读取专项 skill。
- 详细规则只保留在主责 skill 中；本技能只保留短摘要和路由。
- 用户当前指令、项目 `AGENTS.md`、现有代码约定优先于通用 skill 默认值。

## 职责地图

| Skill | 主职责 | 不负责 |
| --- | --- | --- |
| `java-backend-api-standard` | HTTP/API 契约、统一响应、错误码、请求头、安全档位、鉴权、防重放、防篡改、幂等、API 合规检查 | 具体业务实现、脚手架生成、代码审查输出格式、Netty 协议细节 |
| `java-backend-project-generator` | 从零生成 Java/Spring Boot Maven 后端项目脚手架和基础模块 | 给已有项目零散加功能、做生产事故修复、定义权威 API 标准 |
| `java-multi-module-architecture` | Maven 多模块、父子 POM、模块职责、依赖方向、模块级 `AGENTS.md`、模块拆分/文档 | 类内部 SOLID 细节、具体业务代码、HTTP 契约细节 |
| `java-development-principles` | SOLID、职责拆分、分层边界、事务、异常、日志、类/方法大小、测试原则 | API 契约细节、脚手架生成、评审报告格式、Netty 协议细节 |
| `java-microservice-dev` | Spring Boot 具体实现：Controller、Service、Mapper/JPA、Feign、MQ、Redis、配置、测试 | 制定全局标准、跨模块重构、风险评审结论、生成新项目骨架 |
| `java-code-review` | Java 代码审查：风险分级、证据、影响、修复建议、测试缺口和输出格式 | 直接实现功能、生成脚手架、事故现场止血 |
| `java-incident-fix` | 生产事故：止血、证据、定位、回滚/热修、验证、RCA 和预防 | 常规需求开发、宽泛重构、脚手架生成 |
| `netty-handler-dispatcher` | Netty TCP/UDP/WebSocket 协议入口、envelope、`func + version`、handler dispatcher、ACK、心跳、连接治理和压测 | 普通 HTTP API 契约权威、Spring Boot 业务实现细节、Maven 多模块拆分 |
| `vibecoding-knowledge-base` | AI 编程知识库、根/模块级 `AGENTS.md`、`docs/vibecoding`、系统边界、模块导航、接口/流程/配置/证据链/风险文档沉淀 | 修改业务代码、改变 API/SQL/配置/测试逻辑、替代 Java 专项 skill 做实现或事故止血 |

## 路由规则

| 用户意图 | Lead skill | Supporting skills |
| --- | --- | --- |
| 新建完整 Java 后端项目 | `java-backend-project-generator` | `java-backend-api-standard`, `java-multi-module-architecture` |
| 新建带 TCP/UDP/WebSocket 入口的项目 | `java-backend-project-generator` | `netty-handler-dispatcher`, `java-backend-api-standard`, `java-multi-module-architecture` |
| 设计或拆分 Maven 多模块项目 | `java-multi-module-architecture` | `java-development-principles`, `java-backend-api-standard` |
| 定义或检查 HTTP/API 标准 | `java-backend-api-standard` | `java-development-principles` |
| 设计或评审 Netty UDP/TCP/WebSocket 协议入口 | `netty-handler-dispatcher` | 落地实现时加 `java-microservice-dev`; 模块归属不清时加 `java-multi-module-architecture`; API 安全字段需统一时加 `java-backend-api-standard` |
| 实现 API、Service、Mapper、Feign、MQ、Redis、配置、测试 | `java-microservice-dev` | `java-development-principles`; API 变更时加 `java-backend-api-standard`; 模块归属不清时加 `java-multi-module-architecture` |
| 控制类/方法大小、SOLID、职责边界、事务、异常、日志、测试 | `java-development-principles` | 需要落地实现时加 `java-microservice-dev` |
| 审查 PR、diff、commit 或已有代码风险 | `java-code-review` | `java-development-principles`, `java-multi-module-architecture`, `java-backend-api-standard` 作为证据来源 |
| 线上故障、紧急 bug、数据/安全风险 | `java-incident-fix` | 热修复时加 `java-microservice-dev`; 修复后加 `java-code-review` |
| 首次生成或完整补齐 AI 编程知识库 | `vibecoding-knowledge-base` | 模块结构不清时加 `java-multi-module-architecture`; API/Netty 事实不清时只把对应专项 skill 作为规则依据 |
| 更新根 `AGENTS.md`、模块级 `AGENTS.md` 或 `docs/vibecoding` | `vibecoding-knowledge-base` | 涉及模块职责边界时加 `java-multi-module-architecture`; 涉及 API 契约说明时加 `java-backend-api-standard` |
| 审查既有知识库是否过期、缺证据或有冲突 | `vibecoding-knowledge-base` | 需要判断代码风险时再加 `java-code-review`; 不直接修改业务代码 |
| 功能实现完成后沉淀架构、接口、流程或 AI 任务模板 | `vibecoding-knowledge-base` | 先由实现类 lead skill 完成代码与验证，再做文档增量更新 |

## 权威规则位置

- API 请求/响应、统一返回、错误码、请求头、安全、鉴权、幂等、防重放、防篡改：`java-backend-api-standard`。
- 类/方法职责、SOLID、分层、事务、异常、日志、测试、文件大小阈值：`java-development-principles`。
- Maven 多模块、`common` 边界、可部署模块依赖方向、模块级 `AGENTS.md`：`java-multi-module-architecture`。
- 具体 Spring Boot 实现方式、数据访问、外部调用、MQ、Redis、配置、实现模板：`java-microservice-dev`。
- 审查严重级别、证据要求、Finding 输出格式：`java-code-review`。
- 事故分级、止血优先级、证据时间线、回滚/热修/RCA 输出：`java-incident-fix`。
- 新项目脚手架 profile、生成脚本参数、生成后验证：`java-backend-project-generator`。
- Netty TCP/UDP/WebSocket 协议 envelope、`func + version`、handler dispatcher、ACK、心跳、连接治理、签名 canonicalization、集群路由和压测：`netty-handler-dispatcher`。
- AI 编程知识库、`AGENTS.md`、`docs/vibecoding`、证据链、系统边界、模块导航和文档完整性收敛：`vibecoding-knowledge-base`。

## 默认工作流

### 新项目

1. 用 `java-backend-project-generator` 生成脚手架。
2. 用 `java-backend-api-standard` 确认 API 契约、安全档位和静态检查。
3. 涉及 Netty 入口时，用 `netty-handler-dispatcher` 确认协议和 handler 边界。
4. 用 `java-multi-module-architecture` 确认模块职责和依赖方向。
5. 用 `java-development-principles` 检查职责拆分、事务、日志和测试底线。

### 既有项目功能开发

1. 读取根和模块 `AGENTS.md`。
2. 模块归属不清时使用 `java-multi-module-architecture`。
3. API 契约新增或变更时使用 `java-backend-api-standard`。
4. 涉及 Netty 传输入口时先使用 `netty-handler-dispatcher`。
5. 具体实现使用 `java-microservice-dev`。
6. 复杂职责、事务、异常、日志或测试判断使用 `java-development-principles`。
7. 运行最小相关构建和测试。

### 代码审查和生产事故

- 代码审查用 `java-code-review` 作为 lead；涉及 Netty 时先检查传输层和 handler 架构。
- 生产事故用 `java-incident-fix` 作为 lead，先止血，再定位根因，再最小热修和复盘。

### 知识库、AGENTS.md 和文档沉淀

1. 用户要求生成、补齐或更新 AI 编程知识库、`AGENTS.md`、模块导航、架构/接口/流程/配置/证据链文档时，使用 `vibecoding-knowledge-base` 作为 lead。
2. 先让 `vibecoding-knowledge-base` 按项目证据确定输出范围；不要把普通功能实现、事故修复或代码审查任务伪装成 docs-only 任务。
3. 如果文档需要解释模块边界，使用 `java-multi-module-architecture` 作为 supporting skill；如果文档需要引用 HTTP/API 规则，使用 `java-backend-api-standard` 作为 supporting skill；如果文档需要引用 Netty 协议规则，使用 `netty-handler-dispatcher` 作为 supporting skill。
4. 如果任务同时要求“实现功能并更新知识库”，先按实现类 lead skill 完成代码、测试和验证，再用 `vibecoding-knowledge-base` 做增量文档更新。

## 执行边界

- 不要把专项技能的大段详细规则复制到本技能。
- 不要为了小需求加载所有 Java/Netty 技能。
- 不要在 docs-only、analysis-only 或 code-review 任务中顺手改业务代码。
- 不要为已有项目引入新的响应包装、数据访问框架、MQ/Redis 客户端或安全框架，除非项目已采用或用户明确要求。

## 实现前说明

修改 Java 代码或 skill 文件前，简短说明：

1. Lead skill 和 supporting skills。
2. 会新增或修改哪些文件。
3. 每个文件的职责。
4. 为什么没有把逻辑放入错误的 skill 或大文件。
5. 验证方式。

## 自检脚本

修改本技能后运行：

```powershell
py "D:\Users\CodexData\.codex\skills\java-backend-development-orchestrator\scripts\check_java_backend_development_orchestrator_skill.py"
```

维护路由规则后运行 `scripts/run_forward_tests.py`；场景定义在 `references/forward-test-scenarios.md`，追加 `--prompts` 可输出可复制给人工或子任务执行的场景 prompt。

## 最终回复

说明：

- 使用的 lead skill 和 supporting skills。
- 修改的文件。
- 行为、文档或标准影响。
- 验证命令。
- 剩余风险或假设。
