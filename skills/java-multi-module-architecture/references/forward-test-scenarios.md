# Forward-test 场景

本文件用于维护 `java-multi-module-architecture` 后做行为验证。普通多模块任务不需要默认读取。

## 场景一：多个模块共用同一个数据库

输入任务：

```text
两个模块调用同一数据库，但业务大多不同，少量表相同。
```

预期关注点：

- 先按业务能力和变更原因拆模块，不按数据库物理连接拆模块。
- 明确共享表的归属模块、访问边界和迁移策略。
- 不把所有 entity、mapper 和 service 都放入 `common`。

### Input Sample

```text
cms-api 和 sdk-api 都访问 order 表，但后台审批和 SDK 下单规则大多不同。
```

### Expected Findings

- rule: 多模块拆分优先按业务能力和变更原因，不按数据库物理连接。
  keyword: 业务能力
- rule: 共享表必须明确归属模块、访问边界和迁移策略。
  keyword: 共享表
- rule: 不把 entity、mapper 和 service 都放入 `common`。
  keyword: `common`

## 场景二：请求把业务代码放进 common

输入任务：

```text
为了复用，把订单、用户和支付的 service 都放进 common。
```

预期关注点：

- 明确拒绝 `common` 污染。
- 建议只放稳定基础设施、DTO 契约或真正跨模块通用能力。
- 易变业务流程留在所属业务模块。

### Input Sample

```text
common 下准备新增 OrderService、UserService、PaymentService。
```

### Expected Findings

- rule: 明确拒绝把易变业务 service 放进 `common`。
  keyword: `common`
- rule: `common` 只放稳定基础设施、DTO 契约或真正跨模块通用能力。
  keyword: 稳定基础设施
- rule: 易变业务流程留在所属业务模块。
  keyword: 所属业务模块

## 场景三：只想分析模块边界

输入任务：

```text
只评估当前多模块结构是否合理，不要改文件。
```

预期关注点：

- 输出模块职责、依赖方向、风险和建议。
- 不运行脚手架，不修改 POM 或 AGENTS.md。
- 如需验证，只建议 `validate-maven-modules.ps1` 或 Maven 命令。

### Input Sample

```text
root/common/cms-api/sdk-api 已存在，只需要审查模块边界。
```

### Expected Findings

- rule: 只评估时输出模块职责、依赖方向、风险和建议。
  keyword: 依赖方向
- rule: 不运行脚手架，不修改 POM 或 AGENTS.md。
  keyword: 不修改 POM
- rule: 验证建议使用 `validate-maven-modules.ps1` 或 Maven 命令。
  keyword: `validate-maven-modules.ps1`
