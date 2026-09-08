# Forward-Test 场景

这些场景用于验证 `$vibecoding-knowledge-base` 是否能在不同压力下选择正确模式、保持业务代码只读、生成有证据链的中文知识库。

## 场景一：快速项目导航不能膨胀成完整工程

### Input Sample

```text
帮我快速看一下这个 Java 后端项目，告诉我模块怎么分、后续 AI 开发应该先读哪些文件。
```

### 预期关注点

- 选择 `quick-map` 或轻量 `standard-kb`，不启动 `full-bootstrap`。
- 输出根目录/模块职责、关键入口、推荐阅读顺序和缺口，不生成大而全的文档树。
- 不修改业务代码、配置、测试或构建文件。

### Expected Findings

- keyword: `quick-map`
- keyword: `模块职责`
- keyword: `推荐阅读顺序`
- keyword: `不修改业务代码`

## 场景二：完整补齐知识库必须有进度和完成门禁

### Input Sample

```text
帮我完整分析这个项目，生成根 AGENTS.md、模块 AGENTS.md 和 docs/vibecoding，继续直到知识库补齐。
```

### 预期关注点

- 选择 `full-bootstrap` 或 `full-completion`。
- 建立或更新进度文档，记录已完成文档、未完成项、待确认项。
- 覆盖系统边界、代码地图、接口索引、核心流程、数据/配置/MQ/Redis 索引、风险、测试和发布建议。
- 完成前进行一致性检查，不能只抽样总结后结束。

### Expected Findings

- keyword: `full-completion`
- keyword: `根 AGENTS.md`
- keyword: `docs/vibecoding`
- keyword: `进度文档`
- keyword: `待确认`
- keyword: `一致性检查`

## 场景三：已有知识库变更只能增量更新

### Input Sample

```text
这个项目已有 docs/vibecoding，现在我只改了登录接口和鉴权配置，帮我更新知识库。
```

### 预期关注点

- 先读取已有知识库和相关代码证据，选择 `incremental-update`。
- 只更新登录接口、鉴权配置、相关流程、风险和待确认项。
- 保留仍然有效的已有内容；发现冲突时记录到文档冲突清单。

### Expected Findings

- keyword: `incremental-update`
- keyword: `保留仍然有效`
- keyword: `登录接口`
- keyword: `鉴权配置`
- keyword: `文档冲突清单`

## 场景四：跨仓依赖必须区分当前事实和外部待确认

### Input Sample

```text
当前仓库会调用用户中心、短信平台和文件服务，帮我梳理跨系统边界和 AI 开发注意事项。
```

### 预期关注点

- 选择 `cross-repo-boundary` 或在 `standard-kb` 中启用跨仓边界分析。
- 当前仓库源码和配置能确认的调用写为事实；外部系统内部行为写入 `待确认`。
- 输出跨系统依赖矩阵、接口/配置证据、风险、确认对象和后续动作。

### Expected Findings

- keyword: `cross-repo-boundary`
- keyword: `跨系统依赖矩阵`
- keyword: `当前仓库可确认事实`
- keyword: `外部系统待确认事实`
- keyword: `确认对象`
