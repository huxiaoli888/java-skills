# 系统架构

## 架构风格

当前项目采用 Maven 多模块的分层单体/多入口后端架构。两个 API 模块可以独立启动和部署，共享公共基础设施库，但各自拥有自己的业务编排和数据库访问边界。

这种结构适合项目早期同时支持后台管理接口和对外 SDK 接口：

- CMS 与 SDK 的 HTTP 契约、认证方式、限流和审计策略可以隔离。
- CMS 与 SDK 如果都访问数据库，mapper、entity、repository 和事务边界分别放在各自 API 模块中。
- 稳定的响应、错误码、trace、安全契约在 `common` 中复用。

## API 标准

统一响应：

```json
{
  "reqid": "client-generated-x-reqid",
  "code": "000000",
  "message": "成功",
  "ts": 1716000000000,
  "data": {}
}
```

通用请求头：

```text
authorization
accept-language
x-trace-id
x-reqid
x-timestamp
x-sign
x-sign-alg
x-api-version
x-udid
```

SDK/开放平台接口额外要求：

```text
x-api-key
```

幂等不使用公共 `idempotencyKey` 请求头或公参，由业务报文中的 `orderNo`、`requestNo`、`businessNo` 等唯一业务键表达。

请求唯一编号由前端或客户端通过 `x-reqid` 请求头传入，服务端校验后写入统一响应 JSON。全局访问日志记录脱敏后的请求体、接口接收到报文的请求时间、返回报文的时间，以及响应 `code` 和 `message`；不记录响应体、`authorization`、签名、secret 或原始 token。

`x-udid` 是登录或鉴权后的会话/设备标识，不要求所有接口一开始就具备。CMS 和 SDK 安全配置提供 `auth-exclude-paths` 和 `udid-exclude-paths`：命中 `auth-exclude-paths` 的接口跳过整体鉴权；命中 `udid-exclude-paths` 的接口仅跳过 `x-udid` 前置校验，不跳过 token、`x-timestamp` 时间窗口或 `x-sign` 验签；未命中配置的接口先判断 `x-udid` 是否为空，为空直接返回统一错误，非空后再进入原有 token 或签名鉴权。

操作审计由 common 按 `common.log.annotation/model/service/aspect` 提供 `OperationAudit` 注解、审计记录、审计服务接口、日志型默认实现和 AOP 切面。CMS 模块默认提供 `OperationAuditService` 的数据库实现，将后台操作写入 `cms_operation_log`，并提供 `cms_login_log` 登录日志表和查询骨架；需要对接外部审计中心时再替换或扩展 `OperationAuditService`。

CORS 由 common 提供统一 `ApiCorsConfiguration` 和 `ApiCorsProperties`。开发环境可以配置本地前端来源，生产环境必须改为明确域名，且携带凭证时禁止使用 `*` 来源。

SQL 注入防护由 common 提供 `SqlInjectionGuard` 和 `SqlInjectionFilter`，只对 query string 和可选 form 参数进行轻量风险拦截。动态字段、排序字段、表名和列名仍必须在业务或 Mapper 层使用白名单映射，SQL 参数值必须使用参数绑定。复杂 SQL 参考 renren 项目做法放入 `src/main/resources/mapper/**/*.xml`，Java Mapper 接口只保留方法签名和参数声明。

可部署 API 模块按环境拆分 `application.yml`、`application-dev.yml`、`application-test.yml` 和 `application-prod.yml`。生产环境必须通过启动参数、环境变量或配置中心覆盖默认 `dev` profile，并替换默认 token、apiKey、secret、CORS 域名、内存请求重放缓存和内存幂等实现。

## 生产级补充标准

- 技术栈、配置中心、Redis、网关、对象存储和监控选型见 `docs/development/production_stack.md`。
- 数据库迁移、操作审计表、幂等表、唯一约束和 SQL 安全见 `docs/development/database_standard.md`。
- CMS 权限码、角色、菜单、数据权限和多租户边界见 `docs/development/permission_standard.md`。
- 分层依赖和 Controller 契约由 ArchUnit 测试兜底，避免 API 模块互相依赖或 controller 直接依赖 entity。
