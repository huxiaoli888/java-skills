# 分层与包结构路由摘要

本文件不维护 Controller、Service、Repository、DTO、事务、异常、日志、测试或文件大小的详细规则。

详细规则由 `java-development-principles` 维护；本文件只保留当前场景下的摘要和路由。

## API 标准接入

- HTTP 请求和响应 DTO、统一响应、错误码、参数校验、安全请求头、签名、防重放和幂等，使用 `java-backend-api-standard`。
- 类和方法职责、分层依赖、事务、异常、日志与测试，使用 `java-development-principles`。
- Maven 模块、`common` 边界和可部署模块依赖方向，使用 `java-multi-module-architecture`。
- Controller、Service、Mapper/JPA、Feign、MQ、Redis 与配置的具体 Spring Boot 落地，使用 `java-microservice-dev`。
