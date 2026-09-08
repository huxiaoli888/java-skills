# 生产替换清单

## 1. 必须替换的开发占位实现

生成器示例中的以下实现只能用于本地开发、演示或最小骨架验证，上生产前必须替换：

| 能力 | 开发占位 | 生产替换 |
| --- | --- | --- |
| CMS token | `default-token: change-me` | 真实登录态、权限系统、短期 token 或统一 SSO |
| SDK 凭证 | 固定 `default-api-key/default-secret` | 数据库、配置中心或开放平台密钥管理 |
| Replay request | `InMemoryReplayRequestStore` | Redis、Tair、KeyDB 或等价高可用缓存 |
| 幂等存储 | 内存记录或示例实现 | 数据库唯一约束 + 状态机 + 响应快照或结果引用 |
| 操作审计 | `LoggingOperationAuditService` | 数据库、审计中心、日志平台或不可变审计存储 |
| 限流 | `InMemoryRateLimiter` 或本地限流 | 网关限流 + Redis/分布式服务端兜底限流 |
| 文件上传 | 扩展名和 content type 基础校验 | 对象存储预签名上传、魔数校验、杀毒/内容扫描、权限化访问 URL |
| 可观测性 | 默认 Actuator 配置 | 公司监控平台、指标采集、告警规则和最小端点暴露 |
| API 文档 | 开发环境 OpenAPI/Swagger UI | 生产关闭，或通过网关/登录态/IP 白名单保护 |
| 权限授权 | 示例 admin principal | RBAC、ABAC、菜单权限、数据权限或统一授权中心 |

## 2. 安全配置替换规则

- 生产环境不得保留 `change-me`、`test-api-key`、`test-secret`、`dev-token` 等默认值。
- 生产替换实现应通过 `ProductionReplacementAutoConfiguration` 或项目等价配置显式启用，不要让开发占位实现和生产实现同时生效。
- JDBC 生产替换应提供真实 `JdbcTemplateIdempotencyRecordRepository` 和 `JdbcTemplateOperationAuditRecordRepository`，并用 H2/MySQL/PostgreSQL 集成测试验证唯一约束、响应快照和审计写入。
- `app.production.replacement.enabled=true` 只能在生产依赖、Redis、数据库审计和幂等表均准备完成后启用。
- 生产环境必须使用 `application-prod.yml` 或配置中心等价配置，并由启动参数、环境变量或配置中心覆盖默认 `dev` profile。
- 生产环境的 token、apiKey、secret、CORS 域名不得写死在代码库中，应来自环境变量、配置中心或密钥系统。
- `auth-exclude-paths` 只允许配置登录、验证码、探活、公开回调握手等明确公开入口。
- `udid-exclude-paths` 只表示跳过 `x-udid` 前置校验，不代表跳过 token 或 `x-sign` 验签。
- SDK/OpenAPI 的 `x-api-key` 与 secret 必须支持禁用、轮换、过期和审计。
- 高风险接口建议增加 IP 白名单、mTLS、调用方状态校验或网关风控。
- 生产 Actuator 不得无保护暴露 `env`、`beans`、`heapdump`、`threaddump`、`configprops`。
- 生产 OpenAPI/Swagger UI 不得公开暴露。

## 3. 日志与审计替换规则

- 访问日志可以异步写入，但不能阻塞主链路过久。
- 请求体写日志前必须经过 `RequestBodyMasker` 或等价策略脱敏。
- `authorization`、`x-sign`、secret、私钥、原始 token 不得写入日志。
- `x-udid` 和 `x-api-key` 默认作为调用身份原值记录，便于排查和审计。
- 关键交易审计不能静默丢失；如果审计系统不可用，必须按项目风险策略选择失败关闭、降级队列或人工告警。

## 4. 幂等与交易替换规则

- 可重试写接口必须从业务报文中提取业务唯一键，例如 `requestNo`、`businessNo`、`orderNo`、`paymentNo`、`callbackNo`。
- 不定义公共 `idempotencyKey` 请求头或公共字段。
- 相同 `businessType + businessKey + requestFingerprint` 可以返回原始结果。
- 相同 `businessType + businessKey` 但不同 `requestFingerprint` 必须返回幂等冲突。
- 订单、支付、退款、回调接口必须有数据库唯一约束和状态机校验，不能只依赖缓存。

## 5. 上线验收

上线前至少验证：

- 固定密钥和内存存储已替换。
- 生产替换自动配置已启用并装配 Redis replay、Redis rate-limit、JDBC 幂等和 JDBC 审计 Bean，或项目已记录等价替代实现。
- CMS 与 SDK 的 `auth-exclude-paths` 和 `udid-exclude-paths` 已最小化配置。
- CMS 和 SDK 受保护接口都已要求 `x-timestamp`、`x-sign`、`x-sign-alg` 和 `x-api-version`；`authorization` 只承载登录后的 token。
- `x-timestamp` 时间窗口、按调用方拆分的 replay key、缓存 TTL、时钟误差和失败策略已明确。
- 请求体脱敏测试、签名验签测试、重放测试、幂等冲突测试和审计测试已通过。
- 限流命中、上传非法类型、上传超限、Actuator 暴露范围和 OpenAPI 生产开关已验证。
