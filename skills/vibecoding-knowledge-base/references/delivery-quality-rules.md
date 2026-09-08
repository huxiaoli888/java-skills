# 交付与质量规则

当项目分析请求可能变得过大、生成索引可能显得过于确定，或未解决项需要治理时，使用本参考文件。

## 交付档位

| 档位 | 目标 | 必需输出 | 停止条件 |
| --- | --- | --- | --- |
| `quick-map` | 帮助用户快速理解项目 | 边界摘要、模块地图、下一步推荐文档 | 用户能识别正确子系统/模块 |
| `standard-kb` | 创建实用型 AI 编码知识库 | 导航、边界、总览、根 AGENTS、关键索引、3-5 个核心流程、风险 | AI 能路由常见需求，并知道剩余待确认项 |
| `full-kb` | 穷尽当前仓库静态证据 | 必需文档、生成索引、模块 AGENTS、P0/P1 流程、状态、冲突、刷新说明 | 完整性状态说明当前仓库静态边界已完成 |
| `deep-dive` | 对一个模块/流程/API 做代码级解释 | 聚焦文档，包含入口、Service 链、状态变化、依赖、风险 | 选定问题可安全实现或评审 |

## 生成索引的必需说明

生成索引必须包含简短说明：

```text
本索引为静态定位结果，用于快速找到入口和代码位置；请求/响应字段、鉴权、幂等、异常分支和运行态配置仍需结合源码实现、配置中心或生产环境确认。
```

仅由正则或注解扫描发现的行使用 `静态定位`。只有阅读实现逻辑后，才使用 `源码确认`。

## 待确认项格式

重要未解决项使用此表格：

| 项目 | 优先级 | 负责人角色 | 确认方式 | 关闭标准 |
| --- | --- | --- | --- | --- |
| 未知内容 | P0/P1/P2/P3 | DevOps/DBA/developer/external-system owner/security/product | command/config console/log/DB query/doc/repo | 所需的准确证据 |

## 模块 AGENTS 最低证据

创建模块 `AGENTS.md` 前收集：

1. 模块目的证据：README、pom、包名、启动类、Controller 名称或既有文档。
2. 运行入口证据：启动类、Controller、listener、schedule，或 “library-only module”。
3. 依赖证据：pom dependency、Feign、mapper/entity 使用、MQ、Redis，或 “none found”。
4. 边界：不应在此模块实现什么。
5. 验证命令，或无法独立构建的原因。

如果无法确认，写 `待确认`，不要用通用文字填充。

## 跨仓库边界检查清单

对于大型系统中的子系统：

| 边界 | 文档 |
| --- | --- |
| 当前仓库拥有 | system boundary |
| 当前仓库不得拥有 | system boundary |
| 兄弟仓库拥有 | external confirmation list |
| 运行态拥有 | external confirmation list |
| 跨系统 sync/API/MQ | external call matrix |
| 文档/代码冲突 | conflict list |

不要让兄弟仓库文档覆盖当前仓库代码。用它们理解意图和归属。
