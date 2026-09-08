# MQ 与 Redis 事故参考

用于 RocketMQ/Kafka 积压、重复消费、毒消息、重试风暴、Redis 热 key、脏缓存、分布式锁失败和缓存雪崩。

## MQ 证据

- Topic、tag、group、queue。
- lag/积压量。
- 消费者错误日志。
- 脱敏后的毒消息样例。
- 下游 DB 或外部调用延迟。
- 重试和死信行为。
- 近期生产者/消费者 payload 变化。

## MQ 止血

- 消费者正在破坏数据时，暂停异常消费者。
- 只有 handler 幂等且下游可承压时，才扩容消费者。
- 隔离毒消息。
- 停用或降级慢下游依赖。
- 重放前确认重复处理策略。

## MQ 常见根因

- handler 因 DB 或外部依赖变慢。
- 消费者反复重试同一条毒消息。
- 发布后 payload 不兼容。
- 缺少幂等。
- consumer group 意外变化。
- topic/tag 配置漂移。

## Redis 证据

- slowlog 和延迟。
- 热 key。
- key TTL 和 value 大小。
- 锁 key 和 owner token。
- 缓存命中率。
- 近期 key 命名或 TTL 变化。

## Redis 止血

- 只有 DB 能承压时才旁路缓存。
- 确认范围后只删除明确有问题的 key。
- 为热 key 增加临时限流。
- 确认 owner-token 行为后再修复锁释放。

## Redis 常见根因

- 缺少 TTL。
- 大量 key 同时过期导致缓存击穿/雪崩。
- 写路径后缓存未正确更新或失效。
- 分布式锁缺少超时或安全 owner token。
- Redis 被当作隐藏事实源。
