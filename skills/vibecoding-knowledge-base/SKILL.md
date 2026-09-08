---
name: vibecoding-knowledge-base
description: Use when Codex needs to analyze an existing project and create or update root AGENTS.md, module-level AGENTS.md, docs/vibecoding, system boundaries, evidence maps, API/flow/config indexes, risk docs, release/testing docs, or AI task templates without modifying business code.
---

# Vibe Coding 知识库

## 概述

使用本技能时，Codex 只分析项目并生成 AI 编码知识库文档，目标是让后续 AI 能更快理解系统边界、模块职责、接口契约、数据流、风险点和开发约束。

所有生成内容默认使用中文；代码标识必须保持原样，包括类名、方法名、包名、接口路径、配置 key、错误码、表名、Redis key、MQ topic、consumer group、bucket、对象 key 等。

## 硬性边界

允许：

- 读取源码、配置、构建文件、SQL、Mapper XML、YAML、properties、README 和已有文档。
- 生成或更新 Markdown 文档。
- 生成或更新根目录 `AGENTS.md`。
- 生成或更新模块级 `AGENTS.md`。

禁止：

- 修改业务代码、接口逻辑、SQL 逻辑、构建逻辑、运行配置或测试代码。
- 删除已有文档或项目文件。
- 重构、格式化或清理无关文件。
- 编造项目中没有证据支撑的模块、接口、表、配置或业务流程。

已有目标文档存在时，必须保留仍然有效的内容，只更新被证据推翻、补强或新增的部分。无法从项目确认的内容标记为 `待确认`，并说明应到哪里确认。

## 执行模式

选择能满足用户请求的最小模式：

| 模式 | 使用场景 |
| --- | --- |
| `quick-map` | 快速了解项目、结构梳理、初步导航 |
| `standard-kb` | 生成可用但不追求穷尽的 AI 知识库 |
| `full-bootstrap` | 第一次完整生成根 `AGENTS.md`、模块 `AGENTS.md` 与 `docs/vibecoding` |
| `full-completion` | 用户明确要求“完整分析、继续直到完成、补齐全部知识库” |
| `incremental-update` | 代码或架构小范围变化后更新已有知识库 |
| `module-deep-dive` | 深入分析某个模块、子系统或业务域 |
| `api-index-only` | 只生成或刷新 Controller、DTO、认证、兼容性等接口索引 |
| `flow-tracing-only` | 只追踪指定业务流程的入口、状态变化、外部依赖和风险 |
| `audit-existing-docs` | 审查已有知识库是否过期、冲突、缺证据 |
| `cross-repo-boundary` | 在多仓或跨系统场景中梳理当前仓库边界与外部依赖 |

当用户说“继续”“按推荐顺序”“把分析做完”时，先读取已有 `docs/vibecoding` 和进度文档；已有知识库则进入 `incremental-update` 或 `full-completion`，没有知识库才进入 `full-bootstrap`。

详细输出矩阵、增量更新规则、扫描命令和大项目分批策略见 `references/mode-update-rules.md`。

## 引用路由

保持本文件作为统一入口，按任务加载最少必要引用：

- `references/mode-update-rules.md`：选择模式、决定输出范围、增量更新、文档元数据、核心流程评分、扫描命令、大项目分批。
- `references/document-templates.md`：生成或刷新 `docs/vibecoding`、接口索引、流程文档、表格索引、风险与证据文档时使用。
- `references/delivery-quality-rules.md`：控制交付等级、静态索引质量、`待确认` 治理、模块 `AGENTS.md`、跨仓子系统分析质量。
- `references/forward-test-scenarios.md`：验证本技能在快速导航、完整补齐、增量更新、跨仓边界场景下是否触发正确行为。

## 质量底线

- 先定义系统边界，再写模块、接口和流程；不要把外部系统行为写成当前系统事实。
- 所有关键结论必须有证据链：源码路径、配置路径、文档路径、SQL/Mapper、接口路径或明确的 `待确认` 来源。
- `待确认` 不是失败，但必须集中管理，说明影响范围、确认对象和后续动作。
- 不要生成空泛占位文档。除非用户明确要求模板，否则每个新文档都必须包含项目证据。
- 涉及状态变化时，必须追踪数据库、缓存、MQ、外部接口、文件对象或配置变更。
- 涉及跨系统调用时，必须区分“当前仓库可确认事实”和“外部系统待确认事实”。
- 涉及风险、发布、兼容性或测试时，必须写清影响面、验证建议和回滚/降级关注点。

## 完整分析门禁

用户明确要求完整分析、完整知识库、继续直到完成、补齐全部文档时，不得只做抽样总结后结束。必须：

1. 建立或更新进度文档，记录已分析模块、已生成文档、未完成项和 `待确认`。
2. 至少覆盖根 `AGENTS.md`、模块级 `AGENTS.md`、系统边界、代码地图、接口索引、核心流程、数据/配置/MQ/Redis 索引、风险与测试/发布建议。
3. 对不能进入的外部仓库或缺失资料，写入 `待确认`，但不能因此阻塞当前仓库已能完成的分析。
4. 完成前进行一致性检查：文档互相引用有效，事实不冲突，`待确认` 已集中归档，文档范围与用户请求一致。

## 文档自检

修改本技能后必须运行：

```bash
py -X utf8 D:\Users\CodexData\.codex\skills\vibecoding-knowledge-base\scripts\check_vibecoding_knowledge_base_skill.py
py -X utf8 D:\Users\CodexData\.codex\skills\vibecoding-knowledge-base\scripts\run_forward_tests.py
```

交付项目知识库时，最终回复只说明：生成/更新了哪些文档、每类文档解决什么问题、剩余 `待确认` 或风险、建议的下一步验证。不要复述大量文档正文。
