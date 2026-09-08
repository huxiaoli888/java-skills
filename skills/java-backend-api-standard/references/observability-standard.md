# 可观测性标准

## 1. 目标

公司级 Java 后端项目必须让一次请求可以被日志、指标、链路追踪和告警稳定关联。可观测性不是后期补丁，必须和统一响应、访问日志、错误码、安全过滤器一起生成。

## 2. 日志标准

访问日志必须包含：

```text
reqid, traceId, method, path, statusCode, code, message,
requestTime, responseTime, durationMs, clientIp, udid, apiKey, requestBody
```

规则：

- `reqid` 进入统一响应 JSON。
- `traceId` 保留在日志、响应头和内部链路追踪中，不进入公开 JSON body。
- 日志不记录 `authorization`、`x-sign`、secret、私钥、原始 token。
- `x-udid` 和 `x-api-key` 默认不脱敏，作为调用身份排查字段。
- `requestBody` 必须先经过 `RequestBodyMasker`。
- 生产推荐结构化 JSON 日志；如果公司日志平台暂不支持 JSON，至少保持 key-value 字段名稳定。
- `error` 级异常日志只用于程序缺陷、依赖异常、协议解析器缺陷、ACK/响应写出失败、审计失败等不可预期问题。参数错误、客户端协议格式错误、未登录、无权限、资源不存在、签名失败、重放请求、幂等冲突等正常业务失败使用稳定错误码、访问日志和 metrics 观察，不打印异常堆栈，避免用异常日志评估健壮性时被业务分支污染。

## 3. 指标标准

每个可部署 API 模块应接入 Actuator 或公司批准的等价能力。

推荐指标：

```text
http.server.requests
api.security.replay.rejected
api.security.signature.invalid
api.rate.limit.rejected
api.idempotency.conflict
api.audit.save.failed
```

规则：

- 指标标签控制基数，不把用户 ID、手机号、完整 URL、订单号直接作为 tag。
- `uri` 使用模板化路径，例如 `/api/v1/cms/users/{id}`。
- 错误码可以作为低基数 tag，但业务单号不能作为 tag。

## 4. 链路追踪标准

- 网关、应用、下游 HTTP/RPC、数据库访问应尽量贯通同一个 `traceId`。
- 优先使用 OpenTelemetry；公司已有 SkyWalking、Zipkin 等平台时遵守公司接入规范。
- 应用收到 `x-trace-id` 时可以复用；缺失时由网关或应用生成。
- 对外响应头可返回 `x-trace-id`，便于前端和调用方报障。

## 5. 生产暴露策略

生产默认只暴露：

```text
health
info
prometheus
```

禁止无保护暴露：

```text
env
beans
heapdump
threaddump
configprops
loggers
```

## 6. 标准组件要求

实现应包含：

- `config/observability.yml`：Actuator 和指标端点配置。
- `logback-spring.xml` 或等价配置：结构化日志。
- `build/observability-dependencies.xml`：Actuator、Prometheus 和可选 OpenTelemetry 依赖片段。
- 生产配置测试：验证 Actuator 暴露范围不包含危险端点。
