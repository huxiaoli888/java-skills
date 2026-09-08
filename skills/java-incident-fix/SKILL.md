---
name: java-incident-fix
description: Use when Java/Spring Boot 生产事故、线上故障、紧急 bug、数据风险、安全密码事件、JVM/DB/MQ/Redis/外部依赖/配置异常需要止血、证据收集、根因定位、回滚、热修、恢复验证或 RCA。
---

# Java 事故修复

用于处理 Java/Spring Boot 生产事故、紧急线上故障、应急修复、数据风险事件与恢复运行手册。

## 目标

本技能负责生产事故止血、证据、定位、回滚/热修复决策、恢复验证、RCA 和预防动作。具体热修复代码实现使用 `java-microservice-dev`；热修复后风险复核使用 `java-code-review`；涉及模块边界时参考 `java-multi-module-architecture`；涉及 API 契约时参考 `java-backend-api-standard`；涉及 Netty 长连接事故时参考 `netty-handler-dispatcher`。

先安全恢复服务，再修复根因，最后预防复发。

代码变更前，优先选择低风险止血措施：

```text
rollback > config toggle > isolation/degradation > minimal hotfix > broad refactor
```

## 事故流程

1. 评估事故等级。
2. 先止血并稳定服务。
3. 收集证据并建立时间线。
4. 按事故类型路由专项排查。
5. 使用日志、指标、链路、代码、配置和近期变更验证根因。
6. 选择回滚、配置修正、隔离或最小热修复。
7. 用技术和业务信号验证恢复。
8. 产出 RCA 与预防动作。

## 严重等级模型

- `SEV-1`：服务中断、数据损坏、安全暴露或重大客户影响。
- `SEV-2`：核心功能不可用、错误率高、严重降级或消息积压。
- `SEV-3`：局部降级、影响有限用户或非关键链路。

若数据完整性或安全性存在不确定性，在证实前按更高等级处理。

## 事故类型路由

| 现象 | 优先检查 | 快速止血 | 根因方向 |
| --- | --- | --- | --- |
| HTTP 500 激增 | 错误日志、近期发布、API/配置变更、异常堆栈 | 回滚、关闭功能、摘除流量 | 空指针、校验缺失、配置漂移、依赖失败 |
| 延迟升高 | APM 链路、慢 SQL、线程池、外部调用耗时、GC | 降级慢依赖、限流、扩容安全组件 | 慢查询、远程超时、锁竞争、GC |
| JVM OOM / Full GC | GC 日志、堆转储、`jcmd`、内存指标 | 确认安全后重启、回滚泄漏版本、削减流量 | 内存泄漏、无界集合、缓存膨胀 |
| CPU 高 | 线程转储、热点线程、热点接口、近期代码 | 限流、停用调度任务或消费者 | 死循环、序列化、正则、重试风暴 |
| 线程池耗尽 | 线程转储、池指标、远程调用、阻塞操作 | 增加隔离、削减流量、补超时、回滚 | 缺少超时、阻塞调用、重试风暴 |
| DB 连接池耗尽 | 连接池指标、活跃 SQL、锁等待、慢查询 | 限流、经批准后终止危险查询、回滚 | 慢 SQL、连接泄漏、事务过大 |
| 数据不一致 | 受影响行、近期写入、事务日志、MQ 状态 | 停写/只读、暂停消费者、备份数据 | 局部提交、重复处理、缺少幂等 |
| MQ 积压 | lag、消费者日志、topic/group、下游耗时 | 暂停异常消费者、扩容消费者、降级下游 | 慢 handler、毒消息、重试循环、DB/外部瓶颈 |
| Redis/缓存异常 | key TTL、热 key、锁 key、Redis 延迟 | 仅删除已批准 key、旁路缓存、削减流量 | 缓存击穿、脏缓存、锁未释放 |
| 外部系统超时 | 客户端日志、超时配置、下游状态 | 降级/兜底、熔断、隔离依赖 | 提供方故障、缺少超时、不安全重试 |
| 配置/Nacos 漂移 | 配置 diff、近期发布、profile/env | 回滚配置、冻结配置变更 | 错误值、缺少默认值、环境不匹配 |
| 安全/密码事故 | 访问日志、鉴权日志、密钥/token 暴露、签名错误 | 吊销/轮换凭据、禁用端点、保留证据 | 鉴权绕过、重放、密钥泄漏、签名流程错误 |

## 先止血

选择最安全的快速动作：

- 回滚到最近的稳定版本
- 关闭功能开关
- 回滚配置
- 停用异常调度任务
- 暂停异常 MQ 消费者
- 降级或隔离外部依赖
- 限流或主动削减流量
- 数据完整性不确定时切换为只读模式

事故进行中不得引入大范围重构。

## 证据采集

尽量采集精确时间戳：

- 首个错误时间
- 受影响 endpoint、service、topic、job 或租户
- 错误码和状态分布
- 近期发布、配置或数据变更
- trace id/request id 样例
- 线程池、DB 连接池、队列 lag、Redis、JVM 和外部调用指标
- 止血动作及观察到的效果

维护时间线。长事故可使用 `planning-with-files` 或 `templates/incident-timeline.md`。

## 专项引用

只加载相关引用：

- `references/jvm-incident.md`：OOM、Full GC、CPU 高、死锁和线程耗尽。
- `references/db-incident.md`：慢 SQL、连接池、锁等待、死锁和数据修复。
- `references/mq-redis-incident.md`：MQ 积压、重复消费、Redis 热 key、缓存和分布式锁。
- `references/external-config-incident.md`：Feign/RPC 超时、重试风暴、Nacos/配置漂移和调度任务问题。
- `references/security-crypto-incident.md`：鉴权绕过、敏感数据泄露、token/key 暴露、SM2/SM3/SM4、签名和重放问题。

## 数据修复规则

任何数据修复前：

1. 用只读查询确认影响范围。
2. 备份受影响数据，或导出精确行集。
3. 必要时停止或隔离持续写入。
4. 准备可幂等执行的数据修复 SQL 或脚本。
5. 评审对应的回滚 SQL 或脚本。
6. 能分批执行时优先小批量执行。
7. 校验修复前后的数量、状态和业务不变量。

没有明确批准和备份时，不得删除或批量更新生产数据。

## 回滚 / 热修复决策树

| 条件 | 首选动作 |
| --- | --- |
| 故障在部署后立即出现 | 优先回滚。 |
| 可关闭单项功能 | 关闭功能开关或配置。 |
| 运行时配置错误 | 回滚配置。 |
| 数据正在被错误写入 | 停止写入或切换为只读。 |
| 外部依赖故障 | 降级、隔离或熔断。 |
| 无法回滚且影响持续较高 | 以明确回滚计划实施最小热修复。 |
| 存在安全暴露 | 关闭受影响路径、轮换凭据或密钥，并保留证据。 |

## 事故期间禁止事项

- 不得进行大范围重构。
- 未经备份和批准不得执行破坏性 SQL。
- 未确认影响范围和恢复方案前，不得清理 MQ/Redis/DB 数据。
- 未制定访问影响计划不得轮换密钥或令牌。
- 不得发布没有回滚计划的热修复。
- 不得将生产密钥、令牌、私钥或原始敏感日志写入文档。
- 不得隐藏不确定性，应明确标记未知项。

## 与其他技能协作

- 长时间事故使用 `planning-with-files` 维护 `task_plan.md`、`findings.md` 和 `progress.md`。
- 具体热修复实现使用 `java-microservice-dev`。
- 使用 `java-development-principles` 保持热修复最小化并遵守分层。
- 热修复后使用 `java-code-review` 审查回归、安全、事务和测试风险。
- 事故关闭后使用 `vibecoding-knowledge-base` 更新运行手册、AGENTS.md、流程文档或风险文档。

## 恢复验证

同时验证技术与业务恢复：

- 错误率
- 延迟
- 吞吐量
- 队列积压
- DB 连接池
- Redis 延迟和键状态
- 外部调用成功率
- 调度任务/消费者状态
- 业务链路端到端验证
- 适用时的数据修正结果
- 告警恢复情况

可用时执行以下快速命令：

```bash
mvn -q -DskipTests compile
mvn test -pl <module> -DskipTests=false
rg -n "ERROR|Exception|traceId|requestId" logs/
```

需要时使用 `scripts/collect-java-incident-info.ps1` 和 `scripts/grep-error-logs.ps1`。

修改本技能后运行：

```powershell
py "D:\Users\CodexData\.codex\skills\java-incident-fix\scripts\check_java_incident_fix_skill.py"
```

维护事故流程后运行 `scripts/run_forward_tests.py`；场景定义在 `references/forward-test-scenarios.md`，追加 `--prompts` 可输出可复制给人工或子任务执行的场景 prompt。

## 输出约定

响应时使用以下结构：

1. `当前严重等级`
2. `影响范围`
3. 按风险和速度排序的 `即时止血选项`
4. `已选动作及原因`
5. `证据 / 时间线`
6. `修复范围`（文件/模块）
7. `验证结果`
8. `回滚计划`
9. `RCA 摘要`
10. `预防动作`（负责人 + 优先级）

正式文档使用：

- `templates/incident-runbook.md`
- `templates/incident-timeline.md`
- `templates/rca-report.md`
- `templates/hotfix-plan.md`
- `templates/rollback-plan.md`
