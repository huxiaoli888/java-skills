# 模式与更新规则

在选择执行范围、更新既有知识库，或分析大型后端项目时使用本参考文件。

## 模式输出矩阵

| 模式 | 更新范围 | 必须读取 | 必须产出/更新 | 不得执行 |
| --- | --- | --- | --- | --- |
| `quick-map` | 整个项目的浅层分析 | 根构建文件、模块树、启动/配置、既有文档 | 简洁系统边界、模块地图、下一步文档建议 | 生成完整索引、模块 AGENTS 或流程深挖 |
| `standard-kb` | 实用深度的项目知识库 | 构建文件、模块树、配置、入口点、既有文档 | 根 `AGENTS.md`、选定模块文档、边界、导航、核心索引、3-5 个核心流程 | 把静态索引伪装成运行态事实 |
| `full-bootstrap` | 整个项目 | 构建文件、模块树、配置、入口点、既有文档 | 根目录 `AGENTS.md`、模块级 `AGENTS.md`、基础 `docs/vibecoding` 文档、索引 | 跳过已启用模块 |
| `incremental-update` | 受影响模块/文档 | 变更文件、相关既有文档、受影响索引 | 仅更新受影响的 `AGENTS.md` 和文档 | 重写无关文档 |
| `module-deep-dive` | 单个模块 | 模块源码/配置/测试/文档、上下游调用 | 模块 `AGENTS.md`、模块地图、流程、风险、状态变化 | 泛化到无关模块 |
| `api-index-only` | API 表面 | Controller、Filter、DTO/VO、Feign Client、协议处理器 | API 索引、入口索引、API 契约文档 | 修改流程文档，除非 API 证据需要 |
| `flow-tracing-only` | 选定流程 | 入口类、Service 链路、数据/MQ/Redis/外部调用 | 流程文档、状态变化、风险说明 | 刷新所有 API 或模块地图 |
| `audit-existing-docs` | 既有文档 | 文档，以及用于抽样核验声明的源码证据 | 冲突清单、过期项、缺失证据、修复建议或小范围文档补丁 | 在没有源码证据时把旧文档当作当前行为 |
| `cross-repo-boundary` | 多仓库系统边界 | 可信外部文档、当前仓库、已知兄弟仓库/配置 | 系统边界、归属地图、跨系统调用矩阵、外部确认清单 | 让外部文档覆盖当前仓库源码事实 |

如果用户没有明确指定模式，选择能满足请求的最小模式。对于 “continue”，从既有进度恢复并使用 `incremental-update`。

## 交付档位

使用交付档位，避免用户只需要轻量答案时过度生成文档。

| 档位 | 使用场景 | 必需输出 | 避免 |
| --- | --- | --- | --- |
| `quick-map` | 用户只想快速理解、项目导览或“这是什么项目” | 1-3 份文档：边界、模块地图、下一步 | 大型生成索引 |
| `standard-kb` | 用户需要可用的 AI 知识库，但没有要求“完整” | 导航、边界、根 `AGENTS.md`、高价值索引、3-5 个核心流程 | 穷尽式流程/代码级追踪 |
| `full-kb` | 用户明确要求完整分析、完整知识库或持续补齐直到完成 | 所有必需文档、生成索引、模块 `AGENTS.md`、P0/P1 流程、状态文件 | 未通过完成门禁就结束 |
| `deep-dive` | 用户询问一个模块、流程、事故或 API | 一个聚焦的模块/流程文档，带代码级证据 | 刷新无关文档 |

如果请求有歧义，从 `standard-kb` 开始，并在完整性/状态文档中记录可选的更深工作，而不是静默扩展到 `full-kb`。

## 增量更新规则

- 在每个更新文档顶部附近记录刷新范围：分析日期、分析模块/文件、证据来源、剩余缺口。
- 文档元数据中的分析范围优先使用可迁移描述，例如仓库相对路径、模块名、流程名、文档类别或 `用户提供的外部系统文档`。
- 不要把某个用户机器上的绝对路径作为唯一分析范围。如果绝对路径有助于追溯，只能放在单独的 `原始参考路径` 字段，并说明该路径仅代表本次分析环境，迁移后需要按实际位置替换。
- 保留用户已写且仍有效的内容。优先追加 `新增发现`、`源码校正` 或 `待确认` 章节，而不是重写。
- 只有当源码、当前配置或更新的可信文档明确冲突时，才替换旧声明。
- 如果某个声明被推翻，保留简短说明：原声明、新证据、影响。
- 当来源发生变化时更新索引：Controller/协议处理器、MQ 生产者/消费者、Redis key、Feign/HTTP Client、定时任务、数据库 Mapper 或启动/配置文件。
- 除非模块职责、启动/测试命令、编码规则或需求到模块的路由发生变化，否则不要刷新 `AGENTS.md`。

## 刷新触发规则

当代码或文档变化时，只刷新匹配文档：

| 变更信号 | 刷新 |
| --- | --- |
| Controller 路径、HTTP 方法、鉴权注解、请求/响应 DTO | `indexes/http_api_index_HTTP接口索引.md`、API 文档 |
| 启动类、Filter、Interceptor、Runner、Schedule、listener | `indexes/entrypoint_index_入口索引.md` |
| Feign client、RestTemplate/WebClient/HTTP client、外部 SDK | `indexes/external_call_matrix_外部调用矩阵.md`、integration 文档 |
| RocketMQ/Kafka producer/consumer/topic/group/tag | `indexes/mq_matrix_MQ生产消费矩阵.md`、受影响流程文档 |
| Redis/cache key、TTL、锁、幂等 key | Redis/cache 文档、状态变化文档 |
| Mapper/XML/entity/table/status field | 数据库 Mapper/表文档、受影响状态变化文档 |
| 模块职责、启动/测试命令、编码规则 | 根目录或模块 `AGENTS.md` |
| 生产风险、事故、鉴权/安全规则 | 风险矩阵、安全文档、发布检查清单 |

如果没有相关来源变化，不要为了让文档树看起来更新而重新生成大型索引。

## 文档元数据

在生成或刷新文档时，如果有帮助，添加紧凑元数据：

```markdown
> 分析时间：YYYY-MM-DD
> 分析范围：仓库相对路径 / module / flow / 用户提供的外部系统文档
> 原始参考路径：可选，仅记录本次分析环境中的绝对路径，迁移后需替换
> 证据来源：源码确认 / 外部文档确认 / 推断 / 待确认
> 当前状态：完整 / 部分完整 / 待人工补充
> 待确认数量：N
```

避免把 `分析范围：E:\user\project\...` 作为唯一范围。推荐写成 `分析范围：当前仓库源码 + ../docs 外部系统文档`；如确实需要，再追加 `原始参考路径：E:\user\project\docs（仅本次分析环境路径）`。

对于 Git 项目，只有在可以本地检查且不会干扰工作区时，才包含当前 commit 或分支。

## 核心流程评分

默认第一批选择 3-5 个最高优先级核心流程作为最小交付范围。

如果用户要求 `完整分析`、`继续补充直到完整` 或 `覆盖所有核心流程`，不要停在 3-5 个流程。继续评分候选项并记录所有 P0/P1 核心流程。

| 信号 | 分数 |
| --- | --- |
| 外部用户/客户端/业务系统入口 | +3 |
| 影响 token、身份、证书、计费、支付、鉴权或权限 | +3 |
| 涉及 Redis、MQ、数据库、对象存储或外部系统副作用 | +2 |
| 热点路径、高流量或延迟敏感协议 | +2 |
| 历史兼容或多版本行为 | +2 |
| 失败具有较大生产影响面 | +3 |
| 难以手工测试或难以恢复 | +2 |

如果两个流程同分，优先选择状态变化更多、跨系统依赖更多的流程。

## 扫描命令

以下命令作为起点，并根据项目语言/框架调整。

Java/Spring:

```bash
rg -n "@SpringBootApplication|SpringApplication.run"
rg -n "@RestController|@Controller|@RequestMapping|@PostMapping|@GetMapping|@PutMapping|@DeleteMapping"
rg -n "@FeignClient|RestTemplate|WebClient|OkHttpClient|HttpClient"
rg -n "@RocketMQMessageListener|RocketMQTemplate|convertAndSend|syncSend|asyncSend|KafkaTemplate|@KafkaListener"
rg -n "RedisTemplate|StringRedisTemplate|opsFor|expire\\(|setIfAbsent|@Cacheable"
rg -n "@Scheduled|implements CommandLineRunner|ApplicationRunner"
rg -n "Mapper|Repository|@Select|@Insert|@Update|@Delete|<select|<insert|<update|<delete"
rg -n "Filter|Interceptor|HandlerInterceptor|OncePerRequestFilter"
```

通用:

```bash
rg --files
rg -n "TODO|FIXME|deprecated|兼容|历史|待确认"
rg -n "topic|consumerGroup|tag|queue|bucket|objectKey|ttl|expire|timeout|retry|compensat"
```

Windows/PowerShell 编码检查:

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Get-Content -Encoding UTF8 <file>
$markers = 0xFFFD, 0x00C3, 0x00C2
$pattern = (($markers | ForEach-Object { [regex]::Escape([char]$_) }) -join '|')
rg -n $pattern <docs-or-skill-path>
```

## 大型项目分批

对于过大、无法一次分析完的项目：

1. 先生成模块地图和入口索引。
2. 对核心流程评分并选择核心流程。
3. 每批分析一个模块或一个流程。
4. 当任务跨多个回合时，将临时笔记保存在 `docs/vibecoding/_work/findings.md`、`progress.md` 和 `open_questions.md`。
5. 将稳定结论合并到正式文档，并把未解决项留在 evidence/conflict 文档中。

## 静态索引质量标签

每个生成索引都应说明证据等级：

| 标签 | 含义 |
| --- | --- |
| `静态定位` | 通过模式或注解扫描发现；适合定位代码，但不足以证明行为。 |
| `源码确认` | 已阅读实现逻辑确认。 |
| `配置确认` | 已由当前仓库配置确认。 |
| `运行态待确认` | 需要 Nacos、DB、Redis、MQ、网关或生产日志确认。 |

脚本生成的索引必须注明哪些字段只是 `静态定位`，哪些需要人工确认。

## 待确认治理

所有 `待确认` 项都应包含：

| 字段 | 含义 |
| --- | --- |
| Priority | 按发布或生产影响标记 P0/P1/P2/P3。 |
| Owner role | Developer、QA、DevOps、DBA、product owner、external-system owner、security owner。 |
| Confirmation method | 命令、配置控制台、DB 查询、日志搜索、会议、文档或外部仓库。 |
| Close criteria | 标记为已确认所需的准确证据。 |

不要让 `待确认` 变成垃圾桶。按优先级排序，并将外部归属项与当前仓库缺口分开。
