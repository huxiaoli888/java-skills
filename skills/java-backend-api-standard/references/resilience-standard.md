# 远程调用与可靠性标准

## 1. 目标

Java 后端项目经常调用配置中心、Redis、数据库、对象存储、支付渠道、短信服务和内部 HTTP/RPC 服务。标准必须定义超时、重试、熔断、隔离和事务边界，避免把远程不确定性藏进数据库事务。

## 2. 基础规则

- 所有远程调用必须有连接超时和读取超时。
- 重试只用于明确幂等的操作。
- 下单、支付、退款、回调状态变更不得无脑重试。
- 不要在长数据库事务中调用不可控远程服务。
- 高风险写操作优先使用业务唯一键、状态机和 outbox/retry job。

## 3. 推荐配置

```yaml
app:
  resilience:
    default-timeout: 3s
    retry:
      enabled: true
      max-attempts: 2
      backoff: 200ms
    circuit-breaker:
      enabled: true
      failure-rate-threshold: 50
      slow-call-duration-threshold: 2s
```

规则：

- 配置必须按下游系统维度可覆盖。
- 熔断、限流、重试命中应打指标。
- 对外开放平台和支付回调的失败处理必须可对账。

## 4. Outbox 与事件

适用场景：

- 数据库状态变更后需要通知外部系统。
- 订单、支付、退款状态变更。
- 审计或消息不能静默丢失。

规则：

- 状态变更和 outbox 记录在同一数据库事务内提交。
- 后台 job 或消息发布器异步投递。
- 投递失败保留可重试记录和告警。
- 消费方仍需幂等。
