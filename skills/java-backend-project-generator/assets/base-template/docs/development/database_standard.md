# 数据库、迁移与幂等存储标准

## 迁移脚本

新项目必须使用 Flyway、Liquibase 或公司批准的迁移机制。推荐目录：

```text
src/main/resources/db/migration
|-- V1__create_cms_log_tables.sql
|-- V2__create_sample_item.sql
`-- V3__create_idempotency_record.sql
```

规则：

- 迁移脚本随代码版本提交。
- 生产环境禁止自动执行未评审的破坏性 DDL。
- 回滚方案必须在发布单或变更说明中体现。

## 业务表统一字段

所有业务表默认包含：

```text
id
create_by
create_time
modify_by
modify_time
version
deleted
```

规则：

- `id` 采用雪花算法生成，数据库字段使用 `bigint`；返回前端时建议转为字符串，避免 JavaScript 大整数精度问题。
- `create_by`、`create_time` 在新增时自动填充。
- `modify_by`、`modify_time` 在新增和修改时自动填充。
- `version` 用于乐观锁，新增默认 `0`，更新时必须在 `where` 条件中校验并递增。
- 使用 MyBatis-Plus 时，`version` 字段必须通过 `@Version` 或等价配置参与乐观锁，且 API 模块必须启用 `OptimisticLockerInnerInterceptor`。
- `deleted` 只表示逻辑删除，`0` 表示正常，`-1` 表示删除，不替代业务状态。
- HTTP Filter 不直接操作数据库字段；Filter 只解析操作者并写入 `OperatorContext`，持久化层通过 `EntityAuditFillSupport` 或 ORM 审计机制自动填充字段。

## 操作审计表

默认 CMS 模块已经生成 `cms_operation_log`，用于后台写操作审计落库和操作日志查询。推荐字段：

```text
id, operation, operation_type, business_id, detail, success,
error_message, trace_id, reqid, request_method, request_uri,
request_time, user_agent, ip, creator_name, create_time
```

规则：

- 不记录原始 `authorization`、secret、签名或原始 token。
- 不默认记录完整请求体和响应体；确需记录时必须脱敏，并避免保存密码、token、验证码、手机号全量等敏感信息。
- 高风险交易审计失败不能静默吞掉。
- `reqid`、`trace_id`、`operation_type + business_id`、`create_time` 应建立索引。

## 登录日志表

默认 CMS 模块已经生成 `cms_login_log`，用于后台登录、登出和登录失败记录。推荐字段：

```text
id, operation, status, user_agent, ip, creator_name,
trace_id, reqid, create_time
```

规则：

- 登录日志只记录登录结果、操作者标识、IP、UA、trace 和 reqid，不记录明文密码、验证码和 token。
- `creator_name`、`status`、`create_time` 应建立索引。
- 当前模板的开发级登录/token 已写入登录成功、失败和登出记录；接入生产级用户、角色和权限体系后仍应统一写入该表。

## 幂等表

推荐唯一约束：

```text
unique(owner_id, business_type, business_key)
```

推荐字段：

```text
owner_id
business_type
business_key
request_fingerprint
status
response_snapshot 或 result_reference
expire_time
create_time
modify_time
```

规则：

- 不定义公共 `idempotencyKey` 请求头或公参。
- `business_key` 来自业务报文，例如 `requestNo`、`businessNo`、`orderNo`、`paymentNo`。
- 相同业务键但不同请求指纹返回幂等冲突。
- 订单、支付、退款还必须在业务表上建立唯一约束。

## SQL 安全

- Mapper 使用 `#{}` 参数绑定。
- `${}` 只能用于服务端白名单映射后的字段、表名或排序方向。
- 分页大小、导出大小、模糊查询长度必须限制。
- 数据权限条件由服务端生成，不信任前端传入的数据范围。

## 复杂 SQL 实现位置

复杂 SQL 参考 renren 项目做法，通过 `src/main/resources/mapper/**/*.xml` 实现：

- 简单单表 CRUD 可继续使用 MyBatis-Plus `BaseMapper`、Wrapper 或简短 Mapper 方法。
- 多表关联、动态查询条件、统计报表、导出列表、数据权限条件和较长 SQL 必须放在 Mapper XML 中。
- Java Mapper 接口只声明方法和参数，不在 `@Select/@Update/@Delete` 注解中堆长 SQL。
- Service 只编排业务规则和事务，不拼接 SQL 字符串。
