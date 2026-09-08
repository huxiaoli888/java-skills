# Java 后端模块路由摘要

本文件只说明 API 标准与模块设计的交界，不维护 Maven 模块、父子 POM、`common` 内容或可部署模块依赖方向的详细规则。

详细规则由 `java-multi-module-architecture` 维护；本文件只保留当前场景下的摘要和路由。

## API 契约接入

- CMS 与 SDK 入口的路由、请求头、统一响应、签名、防重放、幂等和错误码使用 `java-backend-api-standard` 的对应 API 契约 reference。
- 入口模块是否拆分、`common` 的稳定共享边界、POM 依赖方向和独立 Netty 运行模块归属，使用 `java-multi-module-architecture`。
- TCP、UDP 或 WebSocket 的 envelope、`func + version`、ACK、心跳、连接状态和协议错误，使用 `netty-handler-dispatcher`。
- 从零生成模块骨架时，使用 `java-backend-project-generator`。
