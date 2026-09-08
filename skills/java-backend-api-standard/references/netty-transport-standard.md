# Netty 传输入口摘要标准

本文件只定义 `java-backend-api-standard` 视角下的 API 契约接入，不维护 Netty 协议或模块实现细节。

详细规则由 `netty-handler-dispatcher` 维护；本文件只保留当前场景下的摘要和路由。

## API 标准接入

- Netty 响应复用 `java-backend-api-standard` 定义的统一错误码和响应语义；具体 Netty 响应写出、ACK 与协议错误处理由 `netty-handler-dispatcher` 维护。
- TCP、UDP、WebSocket 的 envelope、签名 canonicalization、防重放、`func + version`、handler dispatcher、心跳、连接治理、路由、观测和压测，使用 `netty-handler-dispatcher`。
- 独立 Netty 模块、`common` 共享边界和模块依赖方向，使用 `java-multi-module-architecture`。
- Handler、Service、事务、异常、日志和测试职责，使用 `java-development-principles`；具体 Spring Boot 集成使用 `java-microservice-dev`。
