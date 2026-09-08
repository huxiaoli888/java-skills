# Java 微服务测试指南

当 Java 微服务任务涉及 API 行为、service 逻辑、持久化、MQ、Redis、外部系统或事务行为时使用本参考。

## 测试选择

| 层 | 优先测试方式 |
| --- | --- |
| Controller | MockMvc 或 WebTestClient |
| Service | JUnit + mock/fake |
| Mapper/Repository | 项目既有 mapper/repository 集成测试风格 |
| 外部客户端 | Mock server 或 mock adapter 边界 |
| MQ 消费者 | payload 驱动的 listener 测试 |
| Redis/缓存 | key、TTL、失效、锁释放测试 |
| 事务/幂等 | 重复请求、回滚、重试、补偿测试 |

## 验证降级

如果运行时依赖不可用：

1. 对受影响模块运行编译。
2. 运行不依赖不可用基础设施的测试。
3. 明确说明不可用依赖。
4. 说明完整环境中应运行的命令。
