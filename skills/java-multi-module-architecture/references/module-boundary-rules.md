# 模块边界规则

## 默认模块类型

| 模块类型 | 常见命名 | 职责 | 是否可部署 |
| --- | --- | --- | --- |
| 父工程 | 根目录 | 依赖版本、插件版本、模块列表 | 否 |
| 公共契约 | `<project>-common` / `<project>-contract` | 稳定 DTO、错误码、常量、配置属性、纯工具 | 否 |
| 核心业务 | `<project>-core` / `<project>-service` | 业务规则、应用服务、领域服务 | 通常否 |
| HTTP 入口 | `<project>-api` / `<project>-connector` | controller、request/response、校验、兼容 | 是 |
| 协议服务 | `<project>-protocol-server` | UDP/TCP/Netty/自定义协议 handler | 是 |
| MQ 消费 | `<project>-consumer` | RocketMQ/Kafka listener、幂等、重试、补偿 | 是 |
| 外部集成 | `<project>-integration` / `<project>-outside-connector` | 第三方 API、超时、降级、脱敏日志 | 视情况 |
| 网关 | `<project>-gateway` | 路由、认证、过滤、限流 | 是 |

## 强拆信号

- 独立启动类、端口、配置或部署产物。
- 独立 MQ consumer group、重试、补偿或削峰策略。
- 不同调用方的 API 契约和兼容风险不同。
- 需要独立扩缩容、回滚或发布节奏。
- 外部系统协议、认证、超时、降级策略明显独立。

## 暂不拆信号

- 只是包名不同，但运行时、依赖和发布节奏一致。
- 只是复用一个 DTO 或工具类。
- 业务边界还不稳定，拆分后可能频繁移动。
- 为了“看起来完整”创建空模块。

## 反模式

- `common` 变成大杂烩，包含 controller、service 实现、MQ consumer 或外部系统实现。
- 可部署模块互相 Maven 依赖，形成隐式单体。
- API request/response 被 MQ 或协议模块直接复用。
- 父 POM 管理运行时地址、业务常量或环境配置。
- 为每个目录都创建 Spring Boot 启动类。
- 新模块没有测试、启动命令和部署说明。
