# 数据库、迁移与幂等存储标准




## 目录

- [1. 目标](#1-目标)
- [2. 迁移工具](#2-迁移工具)
- [3. 表与字段命名](#3-表与字段命名)
- [4. 操作审计表标准](#4-操作审计表标准)
- [5. 幂等表标准](#5-幂等表标准)
- [6. 订单/支付唯一约束](#6-订单支付唯一约束)
- [7. SQL 安全规则](#7-sql-安全规则)
- [8. 上线前验证](#8-上线前验证)

## 1. 目标

本标准约束 Java 后端项目中的数据库表设计、迁移脚本、审计字段、唯一约束和幂等存储。API 层的幂等和防重放不能只停留在 Filter 或内存缓存，必须在数据库层有可验证约束。

## 2. 迁移工具

推荐使用：

```text
Flyway 或 Liquibase
```

规则：

- 新项目必须有数据库迁移目录，不允许只依赖手工 SQL。
- 迁移脚本随代码版本提交。
- 生产环境禁止自动执行未评审的破坏性 DDL。
- 回滚方案必须在发布单或变更说明中体现。

推荐目录：

```text
src/main/resources/db/migration
|-- V1__init_schema.sql
|-- V2__create_operation_audit.sql
`-- V3__create_idempotency_record.sql
```

## 3. 表与字段命名

默认规则：

- 表名使用小写下划线，例如 `sys_user`、`operation_audit_log`。
- 字段名使用小写下划线，例如 `create_time`、`modify_by`。
- 主键推荐 `id`，使用雪花算法生成，数据库类型为 `bigint`。
- 公开给前端的大整数 ID 使用字符串返回，避免 JavaScript 精度丢失。
- 时间字段统一使用 `datetime(3)`、`timestamp(3)` 或项目批准类型。
- 金额字段使用最小货币单位整数，或明确 scale 的 `decimal`。

业务表统一字段：

```sql
id
create_by
create_time
modify_by
modify_time
version
deleted
```

规则：

- `create_by`、`create_time` 在新增时自动填充。
- `modify_by`、`modify_time` 在新增和修改时自动填充。
- `version` 用于乐观锁，新增默认 `0`，更新时必须在 `where` 条件中校验并递增。
- 使用 MyBatis-Plus 时，`version` 字段必须通过 `@Version` 或等价配置参与乐观锁，且 API 模块必须启用 `OptimisticLockerInnerInterceptor`。
- `deleted` 仅表示逻辑删除，`0` 表示正常，`-1` 表示删除，不得替代业务状态。
- HTTP Filter 不直接操作数据库字段；Filter 只解析操作者并写入 `OperatorContext`，持久化层通过 `EntityAuditFillSupport`、MyBatis/MyBatis-Plus 拦截器、JPA Auditing 或统一 Repository 基类自动填充字段。
- 业务状态使用明确枚举字段，例如 `status`。

## 4. 操作审计表标准

推荐表结构：

```sql
create table operation_audit_log (
  id bigint primary key,
  reqid varchar(64) not null,
  trace_id varchar(128),
  operator varchar(128),
  operation_type varchar(64) not null,
  business_id varchar(128),
  success boolean not null,
  failure_code varchar(32),
  failure_message varchar(512),
  client_ip varchar(64),
  duration_ms bigint,
  summary varchar(1024),
  create_time timestamp not null
);

create index idx_operation_audit_reqid on operation_audit_log(reqid);
create index idx_operation_audit_operator_time on operation_audit_log(operator, create_time);
create index idx_operation_audit_business on operation_audit_log(operation_type, business_id);
```

规则：

- 审计表不记录原始 `authorization`、`x-sign`、secret 或原始 token。
- `udid` 和 `apiKey` 可作为调用身份原值记录。
- 高风险交易审计失败时，不能静默吞掉。

## 5. 幂等表标准

推荐表结构：

```sql
create table idempotency_record (
  id bigint primary key,
  owner_id varchar(128) not null,
  business_type varchar(64) not null,
  business_key varchar(128) not null,
  request_fingerprint varchar(128) not null,
  status varchar(32) not null,
  response_snapshot text,
  result_reference varchar(256),
  expire_time timestamp not null,
  create_time timestamp not null,
  modify_time timestamp not null,
  constraint uk_idempotency_business unique(owner_id, business_type, business_key)
);

create index idx_idempotency_expire_time on idempotency_record(expire_time);
```

规则：

- 不使用公共 `idempotencyKey` 入参。
- `business_key` 来自业务报文字段，例如 `requestNo`、`businessNo`、`orderNo`、`paymentNo`。
- 相同 `owner_id + business_type + business_key + request_fingerprint` 可返回原始结果。
- 相同 `owner_id + business_type + business_key` 但 `request_fingerprint` 不同，返回幂等冲突。
- 订单、支付、退款还必须在业务表上建立唯一约束，不能只依赖幂等表。

## 6. 订单/支付唯一约束

示例：

```sql
alter table payment_order
  add constraint uk_payment_merchant_order unique(merchant_id, merchant_order_no);

alter table payment_callback
  add constraint uk_payment_callback unique(channel_code, callback_no);
```

规则：

- 外部业务单号必须有唯一约束。
- 状态流转必须在 `where` 条件中校验当前状态。
- 金额、币种、调用方、业务单号必须在状态变更前校验一致。

## 7. SQL 安全规则

- Mapper 使用 `#{}` 参数绑定。
- 复杂 SQL 参考 renren 项目做法，通过 `src/main/resources/mapper/**/*.xml` 实现，不在 service、repository 或 Mapper 注解中拼接长 SQL 字符串。
- `${}` 只能用于服务端白名单映射后的字段、表名或排序方向。
- 分页大小、导出大小、模糊查询长度必须限制。
- 数据权限条件必须由服务端生成，不得信任前端传入组织、租户或用户范围。
- 全局异常不得向客户端暴露 SQL、表名、字段名、数据库类型或堆栈。

## 8. 上线前验证

- 迁移脚本已评审并在测试环境执行。
- 幂等表和关键业务表唯一约束存在。
- 审计表可查询且不会记录敏感密钥。
- 复杂 SQL 已放入 Mapper XML，并完成参数绑定、白名单和数据权限条件评审。
- Mapper 没有直接使用前端值拼接 `${}`。
- 慢 SQL、连接池、索引和事务边界已检查。
