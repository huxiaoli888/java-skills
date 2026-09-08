# 数据库持久化模板

## 统一字段

所有业务表默认包含以下字段：

```text
id
create_by
create_time
modify_by
modify_time
version
deleted
```

字段规则：

| 字段 | 数据库类型建议 | Java 字段 | 说明 |
| --- | --- | --- | --- |
| `id` | `bigint` | `Long id` | 雪花算法主键；返回前端时建议转为字符串 |
| `create_by` | `varchar(64)` | `String createBy` | 创建人，新增时填充 |
| `create_time` | `datetime(3)` | `Instant createTime` | 创建时间，新增时填充 |
| `modify_by` | `varchar(64)` | `String modifyBy` | 修改人，新增和修改时填充 |
| `modify_time` | `datetime(3)` | `Instant modifyTime` | 修改时间，新增和修改时填充 |
| `version` | `bigint` | `Long version` | 乐观锁版本，新增默认 `0`，更新时校验并递增 |
| `deleted` | `int` | `Integer deleted` | 逻辑删除标识，`0` 正常，`-1` 删除 |

## 后端填充边界

HTTP Filter 不直接操作数据库字段。推荐链路：

```text
CMS/SDK Filter -> OperatorContext -> Repository/Mapper/JPA Auditing -> BaseEntity
```

规则：

- `RequestTraceLogFilter` 从 `x-udid` 或 `x-api-key` 提取当前操作者，写入 `OperatorContext`。
- `BaseEntity.id` 使用 MyBatis-Plus `@TableId(type = IdType.ASSIGN_ID)` 生成。
- `EntityAuditFillSupport` 只负责给 `BaseEntity` 填充 `create_by/create_time/modify_by/modify_time/version/deleted`，不手动生成 `id`。
- 接入 MyBatis、MyBatis-Plus 或 JPA 后，应在对应持久化拦截器中调用 `EntityAuditFillSupport`。
- 使用 MyBatis-Plus 时，common 模块通过 `mybatis-plus-annotation` 给 `BaseEntity.version` 声明 `@Version`，拥有数据库访问的 API 模块配置 `MybatisPlusInterceptor` 和 `OptimisticLockerInnerInterceptor`。
- 查询默认带 `deleted = 0`。
- 删除默认执行逻辑删除：`deleted = -1`，不直接物理删除。

## Mapper SQL 示例

新增：

```sql
insert into sample_item (
  id, name, code, description, enabled,
  create_by, create_time, modify_by, modify_time, version, deleted
) values (
  #{id}, #{name}, #{code}, #{description}, #{enabled},
  #{createBy}, #{createTime}, #{modifyBy}, #{modifyTime}, #{version}, #{deleted}
);
```

修改：

```sql
update sample_item
set name = #{name},
    code = #{code},
    description = #{description},
    enabled = #{enabled},
    modify_by = #{modifyBy},
    modify_time = #{modifyTime},
    version = version + 1
where id = #{id}
  and version = #{version}
  and deleted = 0;
```

逻辑删除：

```sql
update sample_item
set deleted = -1,
    modify_by = #{modifyBy},
    modify_time = #{modifyTime},
    version = version + 1
where id = #{id}
  and version = #{version}
  and deleted = 0;
```

查询：

```sql
select id, name, code, description, enabled,
       create_by, create_time, modify_by, modify_time, version, deleted
from sample_item
where deleted = 0
order by modify_time desc;
```
