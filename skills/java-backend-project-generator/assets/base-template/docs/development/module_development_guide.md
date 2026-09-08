# 模块开发指南

## 新增 CMS 接口

1. 在 `chaken-ai-test-cms-api` 新增 controller、request、response。
2. CMS 业务编排、mapper、entity、repository 放入 `chaken-ai-test-cms-api`。
3. 返回 `ApiResult<T>`，不要直接返回 entity、Map 或字符串。
4. 参数校验 message 使用 i18n key。
5. 敏感后台接口必须按 `docs/development/permission_standard.md` 定义权限码、角色和数据权限。

## 新增 SDK 接口

1. 在 `chaken-ai-test-sdk-api` 新增 controller、request、response。
2. 敏感写接口接入签名、防重放和业务幂等。
3. GET 签名使用规范化 query；POST JSON 签名使用 HTTP 原始 body 字节；CMS form-urlencoded 签名使用 HTTP 原始 form body bytes，不使用反序列化后的 Java 对象签名。
4. 业务幂等由业务唯一键表达，例如 `requestNo`、`businessNo`、`orderNo`。

## 新增共享能力

- 稳定公共契约放入 `chaken-ai-test-common`。
- 易变业务流程放入拥有该接口的 API 模块。
- 数据库访问放入实际调用数据库的模块；如果 CMS 和 SDK 都调用数据库，则各自模块分别维护 mapper、entity、repository 和事务边界。
- 只有确认存在稳定、跨 API 共享且不属于单一入口的业务能力时，才新增独立业务库模块。
- 不允许可部署 API 模块互相依赖。
- 跨模块访问日志、请求体脱敏、签名验签、防重放、操作审计等基础设施放入 `chaken-ai-test-common`。
- 后台接口需要操作审计时，在 controller 或 service 方法上使用 `common.log.annotation.OperationAudit`；CMS 模块默认通过 `DbOperationAuditService` 写入 `cms_operation_log`，`common.log.service.LoggingOperationAuditService` 只作为没有业务实现时的兜底。
- 前端跨域统一通过 `chaken.web.cors` 配置，不要在 controller 上零散添加 `@CrossOrigin`。
- 查询、排序、导出等接口不得把前端字段直接拼到 SQL；动态字段必须做白名单映射，SQL 参数值必须使用参数绑定。

## 修改配置

- 通用配置放在 `application.yml`。
- 本地开发差异放在 `application-dev.yml`。
- 测试环境差异放在 `application-test.yml`。
- 生产环境差异放在 `application-prod.yml`。
- 配置项含义和生产替换要求见 `docs/development/configuration_guide.md`。
- 公司级生产技术栈和配置中心规则见 `docs/development/production_stack.md`。
- 数据库迁移、幂等表、审计表和唯一约束见 `docs/development/database_standard.md`。
- CMS 权限、菜单、角色、数据权限和多租户边界见 `docs/development/permission_standard.md`。

## 运行测试

- 公共基础设施测试放在 `chaken-ai-test-common/src/test/java`。
- CMS/SDK 生产配置策略测试放在对应 API 模块。
- 分层和 Controller 契约通过 ArchUnit 测试约束。
- 新增数据库、权限或接口安全能力时，应同步补充对应测试。
