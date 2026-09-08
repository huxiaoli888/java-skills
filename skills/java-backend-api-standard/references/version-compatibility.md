# 版本兼容矩阵标准

## 1. 目标

本文件用于新建 Java/Spring Boot 项目前固定公司级版本基线，避免为了追新版本导致 Spring Cloud、Nacos、MyBatis-Plus、OpenAPI 或监控组件不兼容。

## 2. 公司默认版本矩阵

| 能力 | 默认版本 | 状态 | 说明 |
| --- | --- | --- | --- |
| JDK | 17 | 已验证 | 新项目默认 JDK 17；只有公司统一升级后才默认 JDK 21。 |
| Maven | 3.9.x | 已验证 | 父 POM 管理插件和依赖版本。 |
| Spring Boot | 4.0.5 | 已验证基础骨架 | 当前脚手架默认版本；已通过 common/cms-api/sdk-api 编译、测试、打包和冒烟。 |
| Spring Boot 3.3.x | 公司稳定替代基线 | 按项目选择 | 当 Spring Cloud、Nacos、网关或三方依赖尚未批准 Boot 4 时，新项目应显式选择公司批准的 3.3.x 小版本。 |
| Spring Cloud | 2025.1.x Oakwood | 候选基线 | 官方兼容矩阵显示 2025.1 对应 Spring Boot 4.0.x。 |
| Spring Cloud Alibaba | 2025.1.0.0 | 候选基线 | 2025.1.x 分支对应 Spring Cloud 2025.1.x、Spring Boot 4.0.x、JDK 17+。 |
| Nacos | 跟随 Spring Cloud Alibaba BOM | 待环境验证 | 不单独写死版本，由 SCA BOM 管理并在公司 Nacos 环境验证。 |
| MyBatis-Plus | 3.5.16 | 候选基线 | MyBatis-Plus 已发布 Spring Boot 4 支持；生成器 CRUD 示例使用 boot4 starter。 |
| H2 | 2.4.x | 测试基线 | 仅用于 CRUD 集成测试，不作为生产数据库。 |
| MySQL Driver | 跟随 Spring Boot BOM 或 MyBatis-Plus 验证版本 | 待环境验证 | 生产以公司 MySQL 版本和驱动验证结果为准。 |
| Redis Client | Spring Data Redis，版本跟随 Spring Boot BOM | 待环境验证 | 生产 Redis 集群、连接池、超时和序列化策略必须单独验证。 |
| OpenAPI | springdoc-openapi 3.x | 候选基线 | Spring Boot 4 项目使用 springdoc 3.x；Boot 3 项目使用 2.8.x。 |

## 3. Spring Boot 4.x 启用条件

只有同时满足以下条件，脚手架才允许默认生成 Spring Boot 4.x：

- 基础 common/cms-api/sdk-api 多模块骨架可以完成 Maven compile、test 和 package。
- Spring Cloud 兼容该 Spring Boot 4.x 小版本。
- Nacos 或 Spring Cloud Alibaba 已发布明确兼容版本。
- MyBatis-Plus、数据库驱动、连接池、OpenAPI、Actuator、Micrometer、安全组件均通过本地编译和接口冒烟测试。
- 公司内部至少有一个非核心业务项目完成测试环境验证。
- 生产发布清单中记录版本选择原因和回滚方案。

## 3.1 当前脚手架验证状态

当前生成器默认：

```text
JDK: 17
Spring Boot: 4.0.5
Maven: 3.9.x
```

该默认值只表示脚手架基础骨架已验证，不等于所有生产系统都必须使用 Boot 4。生产系统应根据 Spring Cloud、Nacos、数据库驱动、安全组件、监控组件和公司发布策略确认最终版本。

已验证：

- 多模块父子 POM 解析。
- common/cms-api/sdk-api 编译。
- 单元测试。
- CMS 与 SDK 模块 package。
- API 标准静态检查。

已固化但仍需公司环境验证：

- Spring Cloud 2025.1.x 与 Spring Boot 4.0.5 在公司网关、配置中心和服务发现链路中的组合。
- Spring Cloud Alibaba 2025.1.0.0 与公司 Nacos 服务端版本、命名空间、鉴权和配置加密方式。
- MyBatis-Plus 3.5.16 与公司 MySQL 版本、分页插件、乐观锁和逻辑删除策略。
- springdoc-openapi 3.x 与 Spring Boot 4.0.5、Jackson 3、生产禁用策略。

## 3.2 官方依据

- Spring Cloud Supported Versions：`https://github.com/spring-cloud/spring-cloud-release/wiki/Supported-Versions`
- Spring Cloud Alibaba 2025.1.x README：`https://github.com/alibaba/spring-cloud-alibaba/blob/2025.1.x/README.md`
- MyBatis-Plus releases：`https://github.com/baomidou/mybatis-plus/releases`
- springdoc-openapi releases：`https://github.com/springdoc/springdoc-openapi/releases`

## 4. 禁止事项

- 不允许只因为 Spring Boot 有新版本就修改公司脚手架默认版本。
- 不允许在父 POM 和子模块重复声明同一依赖版本。
- 不允许 CMS API、SDK API 各自使用不同 Spring Boot 或 Spring Cloud 版本。
- 不允许在生产系统中使用未验证的 starter、分页插件或网关插件。

## 5. 项目输出要求

新建项目时必须在规划或 README 中说明：

- JDK 版本。
- Spring Boot 版本。
- Spring Cloud / Spring Cloud Alibaba / Nacos 版本。
- MyBatis-Plus 或 MyBatis 版本。
- OpenAPI、Redis 客户端、数据库驱动和监控组件版本。
- 选择这些版本的兼容依据。
