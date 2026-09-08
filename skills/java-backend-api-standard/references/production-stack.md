# 公司级生产技术栈标准




## 目录

- [1. 目标](#1-目标)
- [2. 默认技术栈矩阵](#2-默认技术栈矩阵)
- [3. Spring Boot 与 Spring Cloud 兼容策略](#3-spring-boot-与-spring-cloud-兼容策略)
- [4. 配置中心规范](#4-配置中心规范)
- [5. Redis 使用规范](#5-redis-使用规范)
- [6. 网关与应用职责边界](#6-网关与应用职责边界)
- [7. 上线前验证](#7-上线前验证)

## 1. 目标

本标准用于新建 Java/Spring Boot 前后端分离项目时固定生产级基础设施选择，避免每个项目自行决定缓存、配置中心、对象存储、监控、日志、API 文档和网关接入方式。

生成器示例中的内存实现和固定密钥只用于本地开发。生产环境必须按本文件选择公司批准的实现。

## 2. 默认技术栈矩阵

| 能力 | 默认选择 | 可选替代 | 生产要求 |
| --- | --- | --- | --- |
| JDK | JDK 17 | JDK 21 | 与 Spring Boot、Spring Cloud、三方 starter 兼容 |
| Spring Boot | 脚手架默认 4.0.5；生产按公司批准矩阵选择 4.0.x 或 3.3.x | 2.x 仅用于存量系统 | 新项目升级前必须验证 Spring Cloud、Nacos 和 MyBatis-Plus 兼容性 |
| 构建 | Maven | Gradle | 父 POM 管理版本和插件，子模块不重复声明版本 |
| 配置中心 | Nacos | Apollo、Spring Cloud Config | 生产配置不写死密钥，按环境隔离命名空间 |
| 服务发现 | Nacos | Kubernetes Service、Eureka | 内部服务调用必须有超时、重试和熔断策略 |
| 缓存 | Redis + Redisson | Tair、KeyDB | replay request、限流、短期缓存必须支持集群和 TTL |
| 数据库 | MySQL/PostgreSQL | Oracle、SQL Server | 使用连接池、迁移脚本、唯一约束和慢 SQL 监控 |
| ORM/SQL | MyBatis-Plus | MyBatis、JPA | 动态字段使用白名单，禁止前端值直接拼 SQL |
| 对象存储 | S3/OSS/MinIO 协议 | 本地文件仅限开发 | 大文件使用预签名上传或分片上传 |
| 网关 | 公司统一 API Gateway | Nginx、Spring Cloud Gateway | 生产 CORS、限流、IP 白名单、TLS 终止优先放网关 |
| 认证 | Spring Security 或公司 SSO | Sa-Token、Shiro | 生产必须接真实用户、角色、权限和会话体系 |
| API 文档 | springdoc-openapi | Swagger2 仅限 Boot 2 | 生产关闭或受保护 |
| 指标 | Actuator + Prometheus | Micrometer 兼容平台 | 生产只暴露必要端点 |
| 链路追踪 | OpenTelemetry | SkyWalking、Zipkin | trace id 必须贯通网关、应用、日志 |
| 日志 | Logback JSON + 日志平台 | Log4j2 | 不记录密钥、签名、原始 token |
| 审计 | 数据库/审计中心 | 日志平台不可变索引 | 关键交易审计不能静默丢失 |
| 可靠性 | 超时 + 幂等 + 状态机 + outbox | Resilience4j、网关熔断 | 远程调用必须有超时，重试只用于幂等操作 |

## 3. Spring Boot 与 Spring Cloud 兼容策略

- 新项目默认不要盲目使用最新 Spring Boot 大版本。
- 当前生成器默认值是 Spring Boot 4.0.5，表示基础骨架已验证；生产项目仍必须按公司兼容矩阵批准。
- 如果公司 Spring Cloud、Nacos、网关或三方 starter 尚未完成 Boot 4 验证，应使用脚手架参数切换到公司批准的 Boot 3.3.x 基线。
- 具体版本选择必须同时遵守 `version-compatibility.md`。
- 如果选择 Spring Boot 4.x，必须先验证 Spring Cloud、Nacos、MyBatis-Plus、springdoc-openapi、数据库驱动、监控组件和安全组件兼容性。
- 如果公司已有 Spring Cloud 版本基线，应以 Spring Cloud 兼容矩阵反推 Spring Boot 版本。
- 对外开放平台、支付、订单等高风险系统，优先选择公司已验证的稳定组合，而不是追最新版本。

## 4. 配置中心规范

推荐 Nacos 命名：

```text
namespace: dev / test / prod
group: {project}
dataId:
  {project}-cms-api.yml
  {project}-sdk-api.yml
  {project}-common.yml
```

规则：

- 本地 `application.yml` 只保留启动所需的最小配置和默认 profile。
- 生产密钥通过环境变量、配置中心加密字段或密钥系统注入。
- `auth-exclude-paths`、`udid-exclude-paths`、CORS 域名、限流规则、上传大小、Actuator 暴露范围必须可配置。
- 配置变更应记录操作审计。

## 5. Redis 使用规范

必须使用 Redis 或等价高可用缓存的场景：

- SDK/OpenAPI replay request。
- 分布式限流。
- 短期验证码、登录失败次数、风控计数。
- 分布式锁仅在确有跨实例互斥需求时使用。

规则：

- 所有 key 必须有项目前缀和业务前缀。
- replay request key 必须设置 TTL，TTL 与重放窗口一致或略长。
- 支付、订单、回调等高风险链路中，Redis 不可用时默认失败关闭。
- 不要只依赖 Redis 实现订单、支付、退款等业务幂等，必须结合数据库唯一约束。

## 6. 网关与应用职责边界

网关优先承担：

- TLS 终止。
- IP 白名单。
- 粗粒度限流和配额。
- CORS 统一策略。
- 请求大小限制。
- OpenAPI/Actuator 生产保护。

应用必须保留：

- 业务认证和授权。
- SDK 签名验签。
- replay request 校验。
- 业务幂等和唯一约束。
- 请求体脱敏日志和操作审计。
- 细粒度业务限流兜底。

## 7. 上线前验证

- 技术栈版本已在公司兼容矩阵中确认。
- 配置中心、Redis、数据库、对象存储、日志平台、监控平台均有生产环境连接配置。
- 固定 token、固定 apiKey/secret、内存 replay request store、内存限流、日志型审计已替换。
- Actuator 和 OpenAPI 生产暴露策略已验证。
- 关键依赖有版本锁定和漏洞扫描记录。
