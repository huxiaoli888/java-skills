# 文档模板

在生成或刷新 `docs/vibecoding` 文档前使用本参考文件。

## 内容要求

`README_AI编程文档导航.md`:

- 目录导览。
- 每类文档解决什么问题。
- 在功能开发、缺陷修复、API 变更、数据库变更、UDP/协议变更和发布前，AI 应该先阅读哪些文档。

`glossary_业务术语表.md`:

- 中文名称。
- 英文/代码命名。
- 业务含义。
- 相关模块。
- 相关 API 或流程。

`architecture/overview_系统总览.md`:

- 整体架构、模块拆分、模块依赖、模块间调用链。
- 技术栈、外部系统、中间件、数据流总览、核心入口。
- Mermaid 架构图。

`business/*.md`:

- 业务目标、触发入口、模块、调用链、类/方法。
- 主流程、异常流程、数据影响、外部/中间件/配置依赖。
- 日志关键字、测试建议、兼容性关注点。

`api/*.md`:

- API 名称、调用方、提供方、路径/方法、请求/响应参数。
- 错误码、幂等性、鉴权、兼容性、请求/响应示例。

`data/*.md`:

- 表、Redis key、MQ topic/group、对象 bucket/key 名称。
- 用途、关键字段、写入/读取位置、生命周期、兼容性影响、敏感数据影响。
- 对于 MQ/对象存储：生产者/消费者、schema/metadata、重试/顺序/死信/补偿、路径规则、上传/下载/删除、过期/清理。

`code_map/*.md`:

- 类名、文件路径、职责、主要方法、调用方、被调用方、相关流程、修改注意事项。
- 优先覆盖 Controller、Service、Mapper/DAO、Job、Filter、Interceptor、DTO、VO、Request 和 Response。

`flows/*.md`:

- 流程描述、触发条件、调用链、状态变化、数据读写、外部调用、中间件交互、异常分支。
- Mermaid sequence diagram 和 flowchart。

`compatibility/*.md`:

- 历史行为、当前行为、兼容原因。
- 接口、字段、协议、配置、SDK 版本、已知问题和修复。
- 如果历史无法确认，标记 `待人工补充`。

`config/*.md`:

- 配置 key、默认值、环境、用途、读取类、修改风险、是否需要重启、配置示例。

`development/*.md`:

- 如何修改 API、业务流程、协议逻辑、数据库字段、MQ topic/tag/group/schema、对象存储路径/metadata、配置、SDK 兼容性。
- 包含修改前检查和修改后检查清单。

`integration/*.md`:

- 内部/外部/SDK/服务侧/协议调用方、权限、边界、不应直接互相调用的系统、边界图。

`security/*.md`:

- 日志规则、敏感字段、脱敏、证书/token/安全要求、鉴权、协议说明、不得记录的内容、排障关键字。

`release/*.md`:

- 发布前检查、配置、数据库、MQ、对象存储、API/SDK/协议兼容、日志检查、回滚条件、回滚步骤、回滚后验证。

`testing/*.md`:

- 本地启动、本地依赖、单元/集成测试、测试数据、mock 请求、协议报文模拟、验证清单、常见问题。

`templates/ai_task_template_AI需求任务模板.md`:

- 背景、目标、涉及模块/API/表、兼容性要求、不得修改的内容、验收标准、测试要求、需要更新的文档。

## 示例表格

入口索引：

| Type | Entry | Module | Class/Method | Caller | Downstream | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| HTTP/UDP/MQ/Schedule | path/topic/job | module | class.method | caller | service/key/topic/system | file:line |

证据地图：

| Claim | Source type | Source location | Confidence | Note |
| --- | --- | --- | --- | --- |
| conclusion | 源码确认/外部文档确认/推断/待确认 | file/class/method/doc | high/medium/low | verification note |

状态变化：

| State object | Create | Read | Update | Delete/Expire | Idempotency | Exception recovery |
| --- | --- | --- | --- | --- | --- | --- |
| Redis key/table/topic/object | class.method | class.method | class.method | TTL/job/method | key/rule | retry/compensation |

MQ 和外部调用矩阵：

| Caller | Provider | Channel | Path/Topic/Group/Tag | Payload | Idempotency | Failure handling | Owner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| module/class | system/module | API/MQ/RPC | endpoint/topic | DTO/message | key/rule | retry/fallback | owner system |

风险矩阵：

| Risk | Severity | Location | Trigger | Blast radius | Detection | Mitigation |
| --- | --- | --- | --- | --- | --- | --- |
| risk summary | P0/P1/P2/P3 | module/class/method | condition | impact | logs/metrics/symptom | action |
