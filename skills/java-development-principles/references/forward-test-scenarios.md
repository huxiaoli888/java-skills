# Forward-test 场景

本文件用于维护 `java-development-principles` 后做行为验证。普通开发任务不需要默认读取。

## 场景一：巨大 Service 继续加分支

输入任务：

```text
在一个 700 行 Service 中继续增加第三种渠道的处理分支。
```

预期关注点：

- 识别文件超过拆分信号，先评估职责是否已经混杂。
- 优先通过接口、strategy、handler map 或 registry 扩展新渠道。
- 不把新业务继续塞进巨大 `if/else` 或 `switch`。

### Input Sample

```java
if ("SMS".equals(channel)) { ... }
else if ("EMAIL".equals(channel)) { ... }
else if ("APP".equals(channel)) { ... }
```

### Expected Findings

- rule: 一个类约超过 600 行且新增不同职责时，应评估拆分。
  keyword: 600 行
- rule: 新渠道优先通过 strategy、handler map 或 registry 扩展。
  keyword: strategy
- rule: 不应继续扩大巨大 `if/else` 或 `switch`。
  keyword: `if/else`

## 场景二：事务中远程调用

输入任务：

```text
在已有 `@Transactional` 方法中保存订单后调用第三方 HTTP 接口，再更新状态。
```

预期关注点：

- 指出远程调用放在数据库事务内会扩大锁持有和失败半径。
- 优先缩短事务，使用 outbox、after-commit、补偿或项目既有可靠消息模式。
- 说明回滚、重试和补偿边界。

### Input Sample

```java
@Transactional
public void submit(Order order) {
    orderMapper.insert(order);
    thirdPartyClient.notify(order);
    orderMapper.updateStatus(order.getId(), "NOTIFIED");
}
```

### Expected Findings

- rule: 不要在数据库事务中执行慢远程调用，除非说明必要性。
  keyword: 事务中远程调用
- rule: DB 写入和外部副作用需要 outbox、after-commit 或补偿设计。
  keyword: outbox
- rule: 必须说明 rollback、retry 和 compensation 行为。
  keyword: compensation

## 场景三：Controller 混合职责

输入任务：

```text
为了快点上线，把参数解析、权限判断、SQL 查询和响应组装都写在 Controller。
```

预期关注点：

- 明确这是职责混杂，应拆到 Controller、Service、Repository/Mapper 和 DTO/Response。
- Controller 只负责输入边界、校验触发和调用 use-case/service。
- 统一响应契约细节路由到 `java-backend-api-standard`。

### Input Sample

```java
@PostMapping("/users")
public Map<String, Object> create(@RequestBody Map<String, Object> body) {
    checkPermission();
    jdbcTemplate.update("insert into user ...");
    return Map.of("status", "SUCCESS");
}
```

### Expected Findings

- rule: Controller 不应混合权限、业务规则、SQL 和响应格式化。
  keyword: Controller
- rule: 按 Controller、Service、Repository/Mapper 和 DTO/Response 分层。
  keyword: Repository
- rule: HTTP/API 统一响应细节以 `java-backend-api-standard` 为权威。
  keyword: `java-backend-api-standard`
