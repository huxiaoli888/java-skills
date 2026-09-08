# 简单 CRUD 实现与评审标准




## 目录

- [1. 目标](#1-目标)
- [2. 推荐文件结构](#2-推荐文件结构)
- [3. 必须生成的接口](#3-必须生成的接口)
- [4. 分层职责](#4-分层职责)
- [4.1 Lombok 使用约定](#41-lombok-使用约定)
- [5. 数据库字段](#5-数据库字段)
- [6. 分页与排序](#6-分页与排序)
- [7. 校验与错误码](#7-校验与错误码)
- [8. 最小测试](#8-最小测试)
- [8.1 MyBatis-Plus CRUD 标准组件要求](#81-mybatisplus-crud-标准组件要求)
- [9. 不适用场景](#9-不适用场景)

## 1. 目标

本标准用于设计、实现或评审后台管理、内部运营或普通业务维护类 CRUD 接口。目标是形成可维护的层次结构，而不是只交付 controller 空壳。

CRUD 实现必须遵守：

- API 契约使用 `ApiResult<T>` 和 `PageResult<T>`。
- Request DTO、response DTO、entity 不复用。
- 数据库访问写在拥有该接口的模块中。
- `common` 只提供稳定基础设施，不放具体业务 mapper、entity、repository 或 service 实现。

## 2. 推荐文件结构

以 CMS 模块中的 `sample-item` 为例：

```text
{project}-cms-api
  src/main/java/{basePackage}/cms/sampleitem
    controller/CmsSampleItemController.java
    dto/request/SampleItemCreateRequest.java
    dto/request/SampleItemUpdateRequest.java
    dto/request/SampleItemPageQuery.java
    dto/response/SampleItemResponse.java
    dto/response/SampleItemDetailResponse.java
    entity/SampleItemEntity.java
    mapper/SampleItemMapper.java
    service/SampleItemService.java
    service/impl/SampleItemServiceImpl.java
    converter/SampleItemConverter.java
  src/main/resources/db/migration/V1__create_sample_item.sql
```

SDK 模块同理放在 `{project}-sdk-api/src/main/java/{basePackage}/sdk/{domain}` 下。

## 3. 必须生成的接口

普通维护类资源默认生成：

```text
GET    /api/v1/cms/{resources}
POST   /api/v1/cms/{resources}
GET    /api/v1/cms/{resources}/{id}
PUT    /api/v1/cms/{resources}/{id}
DELETE /api/v1/cms/{resources}/{id}
```

规则：

- `GET` 分页查询使用 `PageQuery` 或 `{Domain}PageQuery`。
- `POST` 创建使用 `Create{Domain}Request`。
- `PUT` 修改使用 `Update{Domain}Request`。
- `DELETE` 默认逻辑删除，不物理删除。
- 新增、修改、删除默认增加 `@OperationAudit` 或等价审计能力。

## 4. 分层职责

Controller：

- 只做 HTTP 参数接收、DTO 校验、调用 service、组装 `ApiResult`。
- 不写 SQL、不直接访问 mapper/repository、不直接操作 entity 审计字段。

Service：

- 持有事务边界。
- 做业务校验、唯一性校验、状态校验和调用 mapper/repository。
- 普通后台 CRUD 默认采用 renren 式单 service 接口，例如 `SampleItemService`，不要为了简单增删改查额外拆 `CommandService`、`QueryService`、`command`、`query`、`model` 包。
- 订单、支付、审批、复杂状态机、多模型聚合等复杂业务可以再按用例拆分 command/query/service，但不作为普通 CRUD 默认模板。

Mapper/Repository：

- 只负责数据库访问。
- 动态字段、排序字段必须使用白名单。
- 参数值使用绑定参数，不拼接前端原值。

Converter：

- 负责 entity/request/response 之间的转换。
- 不访问数据库，不做认证鉴权。

## 4.1 Lombok 使用约定

DTO、VO、Query 和 Entity 可以使用 Lombok 减少样板代码，但必须遵守以下规则：

- Request/Response DTO 推荐使用 `@Getter`、`@Setter`、`@NoArgsConstructor`。
- Entity 推荐使用 `@Getter`、`@Setter`，不要默认使用 `@Data`。
- 包含 token、secret、password、authorization、signature 等敏感字段的类禁止使用会自动输出全部字段的 `@ToString`。
- 禁止为了链式写法牺牲清晰的构造边界；复杂创建逻辑放在 converter 或 service 中。
- 如果团队或项目禁用 Lombok，生成器必须退回显式 getter/setter，不影响 API 契约。

依赖由父 POM 或公共构建配置统一管理，子模块不要重复声明 Lombok 版本。

## 5. 数据库字段

业务表必须包含统一字段：

```sql
id bigint primary key,
create_by varchar(128) not null,
create_time timestamp not null,
modify_by varchar(128) not null,
modify_time timestamp not null,
version bigint not null,
deleted int not null
```

规则：

- `id` 使用雪花算法生成。
- `create_by/create_time/modify_by/modify_time/version/deleted` 由持久化层自动填充。
- HTTP Filter 只把操作者写入 `OperatorContext`，不直接操作数据库字段。
- `deleted=0` 表示正常，`deleted=-1` 表示删除。
- 更新时必须校验并递增 `version`。

## 6. 分页与排序

分页响应统一使用：

```java
PageResult<T>
```

内存列表或测试样例分页使用：

```java
PageSupport.ofList(all, page, pageSize)
```

数据库分页由 ORM、分页插件或 SQL 完成，但必须复用同一套页码语义：

- `page` 从 `1` 开始。
- `pageSize` 必须有上限。
- `sort` 字段必须映射到服务端白名单。
- 不向前端暴露未文档化的数据库列名。

## 7. 校验与错误码

- Request DTO 字段必须使用 Bean Validation。
- 校验 message 使用 i18n key。
- 唯一约束冲突使用稳定业务错误码，不直接暴露 SQL 异常。
- 查询不存在返回 `AC0004` 或项目定义的资源不存在错误码。
- 乐观锁失败返回明确的并发修改错误码。

## 8. 最小测试

普通 CRUD 至少覆盖：

- controller 统一响应格式。
- 参数校验失败。
- 创建成功。
- 分页查询成功。
- 详情不存在。
- 修改乐观锁失败。
- 删除后查询不到。
- mapper 动态排序字段白名单。

## 8.1 MyBatis-Plus CRUD 标准组件要求

使用 MyBatis-Plus 时，生成器示例或项目实现至少包含：

- `entity/{Domain}Entity.java`：继承 `BaseEntity`，使用 `@TableName` 声明表名，使用 Lombok `@Getter/@Setter`，业务字段按需要补充 `@Schema`。
- `mapper/{Domain}Mapper.java`：继承 `BaseMapper<Entity>`，只放本实体查询。
- `service/{Domain}Service.java`：普通后台 CRUD 的统一业务入口，直接承载分页、详情、新增、修改、删除方法。
- `service/impl/{Domain}ServiceImpl.java`：事务边界、唯一性校验、逻辑删除、乐观锁。
- `converter/{Domain}Converter.java`：DTO、entity、response 转换。
- `config/MybatisPlusConfiguration.java`：配置 `MybatisPlusInterceptor` 和 `OptimisticLockerInnerInterceptor`。
- `db/migration/Vxxx__create_{domain}.sql`：建表、唯一索引、逻辑删除字段、乐观锁字段。

动态排序必须通过服务端白名单映射为数据库列名，禁止前端字段直接进入 SQL。

复杂 SQL 参考 renren 项目做法，通过 Mapper XML 实现：

- 简单单表 CRUD 可继续使用 MyBatis-Plus `BaseMapper`、Wrapper 或简短 Mapper 方法。
- 多表关联、动态查询条件、统计报表、导出列表、数据权限条件和较长 SQL 必须放在 `src/main/resources/mapper/**/*.xml`。
- Java Mapper 接口只声明方法和参数，不在 `@Select/@Update/@Delete` 注解中堆长 SQL。
- Service 只编排业务规则和事务，不拼接 SQL 字符串。

`BaseEntity` 必须声明数据库映射注解：

- `id` 使用 `@TableId(type = IdType.ASSIGN_ID)`。
- `createBy/createTime` 使用 `@TableField(fill = FieldFill.INSERT)`。
- `modifyBy/modifyTime` 使用 `@TableField(fill = FieldFill.INSERT_UPDATE)`。
- `version` 使用 `@Version`。
- `deleted` 使用 `@TableLogic(value = "0", delval = "-1")`。

如果 `version`、`deleted` 等字段继承自 common 的 `BaseEntity`，common 模块必须引入 `mybatis-plus-annotation`。真正访问数据库的 API 模块负责 MyBatis-Plus starter、Flyway、分页/乐观锁/防全表更新插件等运行时配置。`MybatisPlusConfiguration` 至少启用 `PaginationInnerInterceptor`、`OptimisticLockerInnerInterceptor` 和 `BlockAttackInnerInterceptor`。

## 9. 不适用场景

以下场景不能直接套普通 CRUD 标准组件：

- 订单、支付、退款、钱包、回调。
- 有复杂状态机的审批流。
- 高并发库存扣减。
- 强一致对账。
- 涉及多租户复杂数据权限的查询。

这些场景必须额外应用 `security.md`、`database-standard.md`、`authz-standard.md` 和高风险交易检查清单。
