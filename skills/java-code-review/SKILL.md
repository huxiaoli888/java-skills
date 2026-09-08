---
name: java-code-review
description: Use when 需要审查 Java/Spring Boot PR、diff、commit 或已有代码变更，重点判断缺陷、回归、兼容性、安全、事务一致性、模块边界、MQ/Redis/外部调用、性能、日志/异常和测试缺口。
---

# Java 代码审查

使用本技能对 Java/Spring Boot 后端代码做风险导向审查。优先关注行为正确性、可靠性、数据安全、安全合规、兼容性、可运维性和测试缺口。除非代码风格会导致真实风险，不要把审查精力花在纯风格问题上。

## 审查目标

发现可能破坏业务行为、降低可靠性、污染或破坏数据、削弱安全/合规能力，或让生产故障更难定位的问题。

本技能只定义审查流程、严重级别、证据要求和 Findings 输出格式。具体 API、分层、事务、模块、微服务实现、事故和 Netty 协议规则，应按问题类型引用对应权威 skill，不在本技能重复展开。

审查结果必须先列 Findings，再写摘要。

## 严重级别

- `P0`：生产故障、数据损坏、凭证/密钥泄露、严重安全漏洞。
- `P1`：高概率缺陷、重大回归、严重兼容性或数据一致性风险。
- `P2`：正确性、可维护性、可运维性或测试风险，应当修复。
- `P3`：有具体风险的小改进；避免纯风格评论。

## 审查流程

1. 确认审查范围：
   - `git diff`、变更文件、commit 或用户提供的 patch。
   - 根目录和模块级 `AGENTS.md`。
   - 构建文件：`pom.xml`、Gradle 文件、依赖变更。
   - 运行配置：YAML/properties/Nacos 占位符。
   - SQL/Mapper XML、entity、DTO、request/response、测试。
2. 分类变更类型：
   - API 契约
   - 业务逻辑
   - 持久化/SQL
   - 事务/幂等
   - MQ/异步
   - Redis/缓存/锁
   - 外部调用/Feign/RPC
   - 安全/密码/签名
   - 配置/部署
   - 仅测试
3. 阅读调用路径，而不是只看变更文件：
   - controller 或 listener 入口
   - service/use-case 层
   - mapper/repository/client
   - DTO/entity/message payload
   - 测试和配置
4. 运行或建议最小有效检查：
   - 编译
   - 受影响模块测试
   - 相关静态辅助脚本
5. 只报告有证据支撑的问题。证据不足时，标注 `low` 置信度，或放入 assumptions/residual risk。

## 优先使用的审查输入

可用且相关时，优先使用以下命令：

```bash
git diff --name-only
git diff --stat
git diff
mvn -q -DskipTests compile
mvn test -pl <module> -DskipTests=false
mvn -pl <module> dependency:tree
```

Gradle 项目使用现有 Gradle wrapper 和等价任务。

## 与其他 Java 技能协作

- 涉及模块归属、父子 POM、可部署模块依赖、`common` 污染或模块级 `AGENTS.md` 时，参考 `java-multi-module-architecture`。
- 涉及 controller/service/repository 分层、SOLID、文件大小、事务边界、异常/日志规则或测试时，参考 `java-development-principles`。
- 涉及 Spring Boot API 实现、MyBatis/JPA、Feign、MQ、Redis、配置、校验或具体测试时，参考 `java-microservice-dev`。
- 涉及 HTTP API 契约、统一返回、错误码、请求头、安全档位、签名、防重放、幂等或 OpenAPI 时，参考 `java-backend-api-standard`。
- 涉及 Netty TCP/UDP/WebSocket 协议入口、handler dispatcher、心跳、ACK、连接状态或协议 envelope 时，参考 `netty-handler-dispatcher`。
- 用户要求处理正在发生的生产事故时，改用 `java-incident-fix`。

## 核心审查维度

| 维度 | 审查重点 | 详细规则 |
| --- | --- | --- |
| API 契约 | path/method/字段/错误码/响应结构兼容性 | `java-backend-api-standard` |
| 业务正确性 | 空值、边界、状态流转、幂等、默认值 | 本技能保留证据要求，复杂实现参考 `java-microservice-dev` |
| 模块边界 | `common` 污染、可部署模块依赖、POM 方向 | `java-multi-module-architecture` |
| 分层与职责 | controller/service/repository/DTO 边界、SOLID、文件大小 | `java-development-principles` |
| 数据一致性 | 事务范围、DB + MQ、重复请求、补偿 | `java-development-principles` 与 `java-microservice-dev` |
| 安全合规 | 鉴权、越权、注入、敏感信息、签名、防重放 | `java-backend-api-standard` |
| 外部依赖 | Feign/RPC、MQ、Redis、配置、超时、重试 | `java-microservice-dev` |
| Netty 协议 | envelope、handler dispatcher、ACK、心跳、连接治理 | `netty-handler-dispatcher` |
| 生产事故修复 | 止血、热修回归、回滚计划、RCA 缺口 | `java-incident-fix` |
| 测试缺口 | 行为变更、负向路径、回滚、幂等、外部失败 | `java-development-principles` |

## 专项参考

只在审查触及对应主题时读取：

- `references/microservice-review.md`：Feign/RPC、MQ、Redis、配置、定时任务、外部调用。
- `references/security-review.md`：鉴权、输入、文件、SSRF、敏感数据、SM2/SM3/SM4、签名、防重放。
- `references/data-consistency-review.md`：事务、幂等、DB + MQ 一致性、补偿。
- `references/testing-review.md`：不同变更类型的测试要求。

## 可选辅助脚本

`java-development-principles` 提供的辅助脚本可以帮助审查：

```powershell
& "C:\Users\03052\.codex\skills\java-development-principles\scripts\check-large-files.ps1" -Path <project>
& "C:\Users\03052\.codex\skills\java-development-principles\scripts\check-java-layering.ps1" -Path <project>
& "C:\Users\03052\.codex\skills\java-development-principles\scripts\check-sensitive-logging.ps1" -Path <project>
```

脚本输出只作为线索，不是最终证据。必须阅读相关代码确认问题。

修改本技能后运行：

```powershell
py "D:\Users\CodexData\.codex\skills\java-code-review\scripts\check_java_code_review_skill.py"
```

维护审查规则后运行 `scripts/run_forward_tests.py`；场景定义在 `references/forward-test-scenarios.md`，追加 `--prompts` 可输出可复制给人工或子任务执行的场景 prompt。

## 输出格式

先输出 Findings，按严重程度排序：

```text
[P1] 简短标题
位置: <file:line>
证据: 具体代码/配置/测试证据
影响: 具体行为、数据、安全、兼容性或可运维性风险
原因: 简要解释
修复: 具体处理动作
建议测试: 应补充或能防止该问题的测试
置信度: high/medium/low
```

然后输出：

- `Assumptions:` 可能影响判断的未知上下文。
- `Residual Risks:` 仍未验证的风险。
- `Test Gaps:` 需要补充的具体测试。
- `Commands Run:` 实际执行的命令，或未执行原因。

## 审查规则

- 不要关注纯风格问题，除非它会造成真实风险。
- 不要提出大规模重构，除非这是修复真实风险的必要条件。
- 不要把猜测当事实报告。
- 不要用通用 skill 默认规则强压项目特定约定。
- 不要为了小问题要求引入新框架或大改架构。
- 如果没有发现问题，明确说明：`No critical findings.`
- 如果不确定，标注 `low/medium/high` 置信度。
