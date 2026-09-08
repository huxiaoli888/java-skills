# 配置说明

## 配置文件结构

每个可部署 API 模块都必须保留以下配置文件：

```text
src/main/resources/
|-- application.yml
|-- application-dev.yml
|-- application-test.yml
`-- application-prod.yml
```

| 文件 | 职责 |
| --- | --- |
| `application.yml` | 通用配置、应用名、context-path、公共安全配置结构、默认 `dev` profile |
| `application-dev.yml` | 本地开发配置，可以使用本地前端来源和开发占位密钥 |
| `application-test.yml` | 测试环境配置，使用测试环境域名和测试密钥占位 |
| `application-prod.yml` | 生产环境配置，敏感值必须来自环境变量、配置中心或密钥系统 |

生产部署必须通过启动参数、环境变量或配置中心覆盖 `spring.profiles.active`，不要依赖 `application.yml` 中的默认 `dev`。

## 通用配置

| 配置项 | 说明 |
| --- | --- |
| `server.port` | 当前 API 模块监听端口 |
| `server.servlet.context-path` | 当前 API 模块上下文路径 |
| `spring.application.name` | 服务名，用于日志、注册中心或链路追踪 |
| `spring.profiles.active` | 默认激活环境，本地模板默认为 `dev` |

## CORS 跨域

配置前缀：

```yaml
chaken.web.cors
```

关键配置：

| 配置项 | 说明 |
| --- | --- |
| `enabled` | 是否启用统一 CORS |
| `path-pattern` | 跨域路径匹配范围 |
| `allowed-origins` | 明确允许的前端来源 |
| `allowed-origin-patterns` | 来源模式，生产环境慎用 |
| `allowed-methods` | 允许的 HTTP 方法 |
| `allowed-headers` | 允许浏览器发送的请求头 |
| `exposed-headers` | 允许浏览器读取的响应头 |
| `allow-credentials` | 是否允许携带凭证 |
| `max-age` | 预检请求缓存时间 |

生产要求：

- `allow-credentials: true` 时禁止使用 `*`。
- 生产环境必须配置明确域名，例如 `https://cms.example.com`。
- CORS 只控制浏览器跨域，不替代 token、签名、防重放或权限控制。

## SQL 注入防护

配置前缀：

```yaml
chaken.security.sql-injection
```

关键配置：

| 配置项 | 说明 |
| --- | --- |
| `enabled` | 是否启用 SQL 注入轻量拦截 |
| `check-query-parameters` | 是否检查 query string |
| `check-form-parameters` | 是否检查表单参数 |
| `exclude-paths` | 排除路径 |

该过滤器只做入口轻量拦截。Mapper 层仍必须使用 `#{}` 参数绑定，动态排序字段、查询字段、表名、列名必须使用服务端白名单。

## CMS 安全配置

配置前缀：

```yaml
chaken.cms.security
```

关键配置：

| 配置项 | 说明 |
| --- | --- |
| `enabled` | 是否启用 CMS 安全过滤器 |
| `signature-enabled` | 是否启用 CMS 受保护接口签名验签 |
| `token-ttl` | 登录生成 Bearer token 的有效期 |
| `default-sign-secret` | 开发占位签名密钥，生产必须替换 |
| `auth-exclude-paths` | 跳过整体认证的路径 |
| `udid-exclude-paths` | 仅跳过 `x-udid` 前置校验的路径 |

生产要求：

- 默认开发管理员和 PBKDF2 密码种子仅用于本地开发；生产必须接入真实用户、角色、菜单、权限和密码策略。
- `default-sign-secret` 必须来自环境变量、配置中心或密钥系统。
- 登录、验证码、探活如果不需要认证，应配置到 `auth-exclude-paths`。
- 只是不具备登录后 `x-udid` 的接口，才配置到 `udid-exclude-paths`。

## SDK 安全配置

配置前缀：

```yaml
chaken.sdk.security
```

关键配置：

| 配置项 | 说明 |
| --- | --- |
| `signature-enabled` | 是否启用 SDK 签名验签 |
| `replay-window` | 防重放时间窗口 |
| `default-api-key` | 开发占位 apiKey，生产必须替换 |
| `default-secret` | 开发占位 secret，生产必须替换 |
| `auth-exclude-paths` | 跳过签名鉴权的路径 |
| `udid-exclude-paths` | 仅跳过 `x-udid` 前置校验的路径 |

生产要求：

- `default-api-key` 和 `default-secret` 必须来自数据库、配置中心、密钥系统或开放平台管理系统。
- 请求重放存储不能使用内存实现，建议替换为 Redis 或等价高速存储。
- 业务幂等不能只依赖内存实现，必须结合数据库唯一约束或持久化幂等记录。

## 限流配置

配置前缀：

```yaml
chaken.security.rate-limit
```

关键配置：

| 配置项 | 说明 |
| --- | --- |
| `enabled` | 是否启用应用内兜底限流 |
| `default-permits` | 默认窗口内允许请求数 |
| `default-window` | 默认限流窗口，例如 `1m` |
| `identity-headers` | 调用身份请求头；CMS 默认使用 `x-udid`，SDK 默认优先 `x-api-key`、`x-udid` |
| `exclude-paths` | 不参与限流的路径 |
| `rules` | 针对登录、导出、下单、支付、回调等敏感路径的规则 |

生产要求：

- `InMemoryRateLimiter` 只适合本地开发或单实例骨架验证。
- 多实例生产环境必须使用网关限流、Redis 或等价分布式限流。
- 限流命中统一返回 `AC0006`。

## 文件上传安全配置

配置前缀：

```yaml
chaken.security.file-upload
```

关键配置：

| 配置项 | 说明 |
| --- | --- |
| `enabled` | 是否启用上传安全策略 |
| `max-bytes` | 单文件最大字节数 |
| `allowed-extensions` | 允许的扩展名 |
| `allowed-content-types` | 允许的 content type |

生产要求：

- 不信任客户端文件名和 content type。
- 服务端必须重新生成对象 key，不能直接使用原始文件名作为存储路径。
- 生产建议增加魔数校验、杀毒/内容扫描、对象存储预签名上传和权限化访问 URL。

## 可观测性配置

配置前缀：

```yaml
management
```

生产要求：

- 默认只暴露 `health`、`info`、`prometheus` 等必要端点。
- 不得无保护暴露 `env`、`beans`、`heapdump`、`threaddump`、`configprops`。
- 健康检查、指标和日志字段应与公司监控平台、日志平台和告警规则保持一致。

## OpenAPI 配置

配置前缀：

```yaml
springdoc
```

生产要求：

- 开发和测试环境可以启用 OpenAPI/Swagger UI。
- 生产环境必须关闭 OpenAPI UI，或通过网关、登录态、IP 白名单等方式保护。
- OpenAPI 注解应与真实 request/response DTO 保持一致。

## 环境差异

| 环境 | 允许内容 | 禁止内容 |
| --- | --- | --- |
| `dev` | 本地端口、本地前端来源、开发 token、开发 apiKey/secret | 真实生产密钥 |
| `test` | 测试域名、测试 token、测试 apiKey/secret | 生产密钥、开发本地来源 |
| `prod` | 环境变量、配置中心、密钥系统 | `change-me`、`dev-*`、`test-*`、`*` CORS 来源 |

## 生产替换清单

上线前必须替换：

- CMS 默认 token。
- SDK 默认 apiKey 和 secret。
- 内存 replay request 存储。
- 内存业务幂等存储。
- dev/test H2 数据源，生产应替换为真实数据库和正式迁移策略。
- P0 示例内存服务实现。
- CORS 示例域名。
- 内存限流实现。
- 文件上传基础校验策略。
- Actuator 生产暴露范围。
- OpenAPI/Swagger UI 生产开关。
