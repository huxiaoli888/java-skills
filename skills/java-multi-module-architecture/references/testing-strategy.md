# 测试分层策略

| 模块类型 | 测试重点 | 推荐测试 |
| --- | --- | --- |
| common | DTO 序列化、常量、工具、配置属性 | JUnit 5 单元测试 |
| core/service | 业务规则、事务边界、状态变化 | 单元测试 + mock repository/client |
| api/connector | HTTP 路径、参数校验、错误码、兼容字段 | MockMvc / WebTestClient / contract test |
| protocol-server | 编解码、报文兼容、异常包处理 | 协议样例包单元测试 |
| consumer | 幂等、重复消息、异常重试、补偿 | listener 单元测试 + mock MQ payload |
| integration/outside | 超时、失败映射、降级、脱敏日志 | WireMock / MockWebServer |
| gateway | 路由、过滤器、认证、限流 | Spring Cloud Gateway 测试 |

## 最小验证

```bash
mvn -q -DskipTests compile
mvn test -pl <module> -DskipTests=false
mvn clean package -pl <module> -am -DskipTests
```

新增模块时至少说明：

- 当前模块是否已有测试。
- 本次是否新增测试。
- 如果未运行测试，原因是什么。
- 环境可用时应该执行哪个命令。
