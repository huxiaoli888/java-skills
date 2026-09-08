# Forward-test 场景

本文件用于维护 `java-microservice-dev` 后做行为验证。普通微服务实现任务不需要默认读取。

## 场景一：新增 POST 接口

输入任务：

```text
在已有 Spring Boot 项目中新增一个创建订单的 POST 接口，要求统一返回和参数校验。
```

预期关注点：

- 先读取现有项目约定，只有没有本地统一响应时才使用模板。
- Controller 保持精简，只做 DTO 校验、读取 `x-reqid` 和调用 service。
- 响应使用 `reqid/code/message/ts/data`，不新增 `status` 或公开 `traceId`。

### Input Sample

```java
@PostMapping("/orders")
public ApiResponse<OrderResponse> create(@Valid @RequestBody CreateOrderRequest request) {
    return ApiResponse.success(orderService.create(request), null);
}
```

### Expected Findings

- rule: 必须把 `x-reqid` 作为 HTTP 请求头传入并原样写入响应。
  keyword: `x-reqid`
- rule: Controller 不应放业务规则、SQL 或远程调用编排。
  keyword: Controller 精简
- rule: 统一响应字段顺序必须保持 `reqid/code/message/ts/data`。
  keyword: `reqid/code/message/ts/data`

## 场景二：Boot2/JDK8 项目

输入任务：

```text
在一个 Spring Boot 2.x、JDK8 项目里补一个全局异常处理器和请求 DTO 校验。
```

预期关注点：

- 使用 `javax.validation.*` 和 `javax.servlet.*`。
- 不使用 `jakarta.*`、`record` 或 `String.isBlank()`。
- 缺少 `x-reqid` 时返回统一错误，不在服务端静默生成 reqid。

### Input Sample

```java
import jakarta.validation.Valid;
record CreateOrderCommand(String orderNo) {}
```

### Expected Findings

- rule: Spring Boot 2.x/JDK8 默认使用 `javax.validation.*`。
  keyword: `javax.validation`
- rule: JDK8 不应使用 `String.isBlank()` 或 Java record。
  keyword: JDK8
- rule: 不要在服务端为 HTTP Controller 请求静默生成 reqid。
  keyword: 静默生成 reqid

## 场景三：签名接口顺序

输入任务：

```text
给 SDK 创建任务接口增加签名校验、防重放和业务幂等。
```

预期关注点：

- 认证鉴权、时间戳窗口、防重放和签名校验顺序遵循项目既有链路和 API 标准。
- 防重放使用 `x-api-key + x-reqid`，业务幂等使用业务字段。
- 不新增 `idempotencyKey` 公共请求头。

### Input Sample

```text
SDK POST /api/v1/sdk/tasks，body 中包含 requestNo。
```

### Expected Findings

- rule: SDK 防重放使用 `x-api-key + x-reqid`。
  keyword: `x-api-key + x-reqid`
- rule: 业务幂等应使用业务字段，例如 requestNo 或 businessNo。
  keyword: 业务幂等
- rule: 不要新增 `idempotencyKey` 公共请求头。
  keyword: `idempotencyKey`
