# 公司级生产技术栈

## 默认选型

| 能力 | 默认选择 | 生产要求 |
| --- | --- | --- |
| JDK | JDK 17 | 与 Spring Boot、Spring Cloud 和三方 starter 兼容 |
| Spring Boot | 3.3.x 或公司批准的 4.x | 选择 4.x 前必须验证 Spring Cloud、Nacos、MyBatis-Plus、springdoc-openapi 等兼容性 |
| 构建 | Maven | 父 POM 管理版本和插件，子模块不重复声明版本 |
| 配置中心 | Nacos | 按 dev/test/prod 隔离命名空间，生产密钥不得写死 |
| 缓存 | Redis/Redisson | replay request、限流、验证码和短期风控计数必须支持 TTL |
| 数据库 | MySQL/PostgreSQL | 使用迁移脚本、唯一约束、连接池和慢 SQL 监控 |
| 网关 | 公司统一 API Gateway | 优先承载 TLS、IP 白名单、粗粒度限流、CORS、OpenAPI/Actuator 保护 |
| 对象存储 | OSS/S3/MinIO 协议 | 大文件使用预签名上传或分片上传 |
| 认证 | Spring Security 或公司 SSO | 生产接真实用户、角色、权限和会话体系 |
| 指标 | Actuator + Prometheus | 生产只暴露 `health`、`info`、`prometheus` 等必要端点 |
| 链路追踪 | OpenTelemetry/SkyWalking | trace id 贯通网关、应用和日志 |

## 配置中心命名

推荐 Nacos 命名：

```text
namespace: dev / test / prod
group: chaken-ai-test
dataId:
  chaken-ai-test-cms-api.yml
  chaken-ai-test-sdk-api.yml
  chaken-ai-test-common.yml
```

## Redis 使用规则

- key 必须有项目前缀和业务前缀。
- replay request key 必须设置 TTL，TTL 与重放窗口一致或略长。
- 支付、订单、回调等高风险链路中，Redis 不可用时默认失败关闭。
- 不要只依赖 Redis 实现业务幂等，必须结合数据库唯一约束。

## 网关与应用边界

网关优先承担 TLS、IP 白名单、粗粒度限流、请求大小限制和文档/诊断端点保护。应用必须保留业务认证、授权、签名验签、防重放、业务幂等、访问日志和操作审计。

## 上线前验证

- 技术栈版本已在公司兼容矩阵中确认。
- 配置中心、Redis、数据库、对象存储、日志平台和监控平台均有生产配置。
- 默认开发管理员、固定 apiKey/secret、内存请求重放缓存、内存限流和日志型兜底审计已替换；CMS `cms_sys_user`、`cms_sys_role`、`cms_sys_menu`、`cms_sys_dict`、`cms_sys_dict_item`、`cms_sys_param`、`cms_admin_token`、`cms_operation_log`、`cms_login_log` 已接入生产数据库和正式迁移策略。
- Actuator 和 OpenAPI 生产暴露策略已验证。
