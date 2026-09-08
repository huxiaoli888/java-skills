# Forward-test 场景

本文件用于维护 `java-code-review` 后做行为验证。普通代码审查不需要默认读取。

## 场景一：PR 同时改 Controller 和 Service

输入任务：

```text
审查一个订单接口 PR，diff 中 Controller 新增参数但 Service 没有处理空值。
```

预期关注点：

- Findings 先行，按 P1/P2/P3 排序。
- 每条 finding 必须包含位置、证据、影响、修复和建议测试。
- 不应直接修改代码。
- 分层、事务或响应契约问题应路由到对应权威 skill 作为依据。

### Input Sample

```java
@GetMapping("/orders")
public ApiResult<List<OrderVO>> list(@RequestParam String channel) {
    return ApiResult.success(orderService.list(channel), reqid);
}
```

### Expected Findings

- rule: Findings 必须先行并按 P1/P2/P3 排序。
  keyword: Findings
- rule: 每条 finding 包含位置、证据、影响、修复和建议测试。
  keyword: 建议测试
- rule: 审查任务不应直接修改代码。
  keyword: 不应直接修改代码

## 场景二：证据不足的性能猜测

输入任务：

```text
审查一个 Redis 缓存改动，只说“可能会慢”。
```

预期关注点：

- 不把猜测当 finding。
- 可以放入 `Residual Risks` 或 `Test Gaps`，标注需要的压测、指标或日志证据。
- 不应提出大规模架构重构。

### Input Sample

```text
diff 只显示新增 Redis get/set，没有耗时指标、QPS、key 数量或慢日志。
```

### Expected Findings

- rule: 证据不足的性能猜测不能作为 finding。
  keyword: 不把猜测当 finding
- rule: 可放入 `Residual Risks` 或 `Test Gaps`。
  keyword: `Test Gaps`
- rule: 不应提出大规模架构重构。
  keyword: 架构重构

## 场景三：无问题但测试缺口存在

输入任务：

```text
审查一个小型字段映射 PR，未发现明显缺陷，但没有负向测试。
```

预期关注点：

- 明确输出 `No critical findings.`。
- 单独列出 `Test Gaps`。
- 不为了凑 finding 报告纯风格问题。

### Input Sample

```text
新增字段 displayName 映射，现有 happy path 测试通过，但没有空值和超长值测试。
```

### Expected Findings

- rule: 无关键缺陷时明确输出 `No critical findings.`
  keyword: `No critical findings.`
- rule: 测试缺口放入 `Test Gaps`。
  keyword: `Test Gaps`
- rule: 不为了凑 finding 报告纯风格问题。
  keyword: 纯风格问题
