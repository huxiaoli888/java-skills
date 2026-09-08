---
name: java-backend-project-generator
description: Use when 需要从零生成 Java/Spring Boot Maven 后端脚手架，按 renren 风格 minimal 后台或 standard profile 创建 common、cms-api、sdk-api，或显式要求 IncludeNetty 生成 TCP/UDP/WebSocket 基础模块。
---

# Java 后端项目生成器

## 目的

使用本技能一次性创建完整 Java 后端项目骨架。本技能面向新项目和项目模板，不用于给已有代码库单独增加一个功能。

本技能只负责新项目脚手架和模板生成，不负责既有项目零散功能开发。生成出的 API、模块和 Netty 骨架必须符合对应权威 skill：API 契约参考 `java-backend-api-standard`，多模块边界参考 `java-multi-module-architecture`，Netty 协议入口参考 `netty-handler-dispatcher`，生成后业务实现由 `java-microservice-dev` 接管。

它会把类似下面的请求：

```text
Generate chaken-order with cms-api and sdk-api.
Generate chaken-order minimal backend.
```

转换为一个完整 Maven 多模块脚手架，并提前准备好接口侧模块。

## 输出 Profile

除非用户明确覆盖，默认使用 `minimal` profile，优先生成 renren 风格的轻量后台基础框架：

```text
{projectName}
|-- {projectName}-common
`-- {projectName}-cms-api
```

依赖方向：

```text
cms-api -> common
```

当用户明确要求“SDK 接口”“开放接口”“CMS + SDK 双入口”或指定 `-Profile standard` 时，才生成：

```text
{projectName}
|-- {projectName}-common
|-- {projectName}-cms-api
`-- {projectName}-sdk-api
```

依赖方向：

```text
cms-api -> common
sdk-api -> common
```

当用户明确要求 TCP 长连接、UDP、Netty 协议入口或类似“长连接服务”时，在 `minimal` 或 `standard` 的基础上额外生成：

```text
{projectName}
`-- {projectName}-netty
```

Netty 模块依赖 `common`，包含 TCP/UDP 启动框架、`func + version` handler dispatcher、AUTH、HEARTBEAT、ACK/统一响应、基础鉴权防篡改占位、全局日志、心跳和基础测试。Netty 模块只在明确启用 `-IncludeNetty` 时生成；默认 `minimal` 和 `standard` 不生成。

当用户明确要求“小项目”“最小后台”或 `-Profile minimal` 时，只生成：

```text
{projectName}
|-- {projectName}-common
`-- {projectName}-cms-api
```

生产增强路线图目前只保留在 `references/profile-design.md`，不是脚本参数；不要承诺它已经具备生产替换和 fail-fast 能力。

不要让可部署 API 模块互相依赖。
数据库调用、实体、mapper、repository 和易变化的业务流程，应放在拥有该接口的 API 模块中。例如，如果 `cms-api` 和 `sdk-api` 都调用数据库，则两个模块各自拥有自己的持久化层，不要共享一个生成的 `core` 模块。

CMS 默认生成后台接口基础框架、后台安全骨架、开发级 `cms.sys` 用户/角色/菜单/权限/字典/参数查询骨架、操作日志/登录日志查询与操作审计落库、P0 查询示例和可选 CRUD 示例；不要默认生成 SDK 调用方应用、SDK 密钥、SDK 调用日志等开放平台管理包。只有用户明确要求“开放平台管理后台”或“SDK 调用方管理”时，才在 CMS 模块中新增独立大域，例如 `cms.openapi` 或 `cms.sdkmanage`。

CMS 业务包按大业务域组织。账号、角色、菜单、权限、部门、参数、字典等后台系统能力统一归入 `cms.sys` 大域，不要默认拆成 `cms.sys.user`、`cms.sys.role`、`cms.sys.menu` 等过细根包；订单类、系统类、开放平台管理类等才作为独立大域。

## 工作流程

1. 推断或接收以下参数：
   - `projectName`
   - `groupId`
   - `basePackage`
   - 输出目录
   - Java 版本，默认 `17`，只支持 Java 17+
   - Spring Boot 版本，默认 `4.0.5`，只支持 Spring Boot 3.x/4.x
   - CMS 端口，默认 `18080`
   - SDK 端口，默认 `18081`
   - Netty HTTP 管理端口，默认 `18082`
   - Netty TCP 端口，默认 `19090`
   - Netty UDP 端口，默认 `19091`
   - 生成 profile，默认 `minimal`，可选 `minimal`、`standard`
   - 是否包含 Netty 模块，默认不包含；用户要求 TCP 长连接或 UDP 时启用

2. 当 PowerShell 可用时，运行 `scripts/scaffold-java-backend-project.ps1`，不要手写生成文件。

3. 只有在用户询问生成器包含哪些内容、想定制生成流程，或生成后的项目需要人工修复时，才读取 `references/generation-workflow.md`。

4. 涉及 `-Profile` 或用户要求“小项目/最小后台/生产就绪”时，阅读 `references/profile-design.md`。当前脚本只支持 `minimal` 和 `standard`；生产增强只保留路线图，不是运行参数，不应承诺已经具备生产替换和 fail-fast 能力。

5. 生成后运行：

```powershell
mvn -q -DskipTests compile
mvn -q -pl <projectName>-cms-api -am -DskipTests package
# 仅 standard profile 执行：
mvn -q -pl <projectName>-sdk-api -am -DskipTests package
# 仅启用 IncludeNetty 时执行：
mvn -q -pl <projectName>-netty -am -DskipTests package
py <api-standard-skill-root>\scripts\check_java_api_standard.py <project-root> --profile <profile> --json --fail-on-error
```

修改生成器脚本、base-template 或 profile 裁剪规则后，还必须运行：

```powershell
py "<skill-root>\scripts\check_java_backend_project_generator_skill.py"
py "<skill-root>\scripts\run_forward_tests.py"
& "<skill-root>\scripts\test-generator-profiles.ps1"
```

6. 汇报生成项目路径、模块、profile、验证结果和剩余生产替换项。

## 脚本用法

```powershell
& "<skill-root>\scripts\scaffold-java-backend-project.ps1" `
  -ProjectName "chaken-demo" `
  -GroupId "com.chaken.demo" `
  -BasePackage "com.chaken.demo" `
  -OutputDir "E:\work\study"
```

可选参数：

```text
-Version
-JavaVersion
-SpringBootVersion
-CmsPort
-SdkPort
-CmsModuleName
-SdkModuleName
-CommonModuleName
-NettyModuleName
-NettyHttpPort
-NettyTcpPort
-NettyUdpPort
-Profile minimal|standard
-IncludeDbCrudExample
-IncludeNetty
```

版本边界：当前 base-template 使用 `record`、`String.isBlank()` 和 `jakarta.*` 包，生成器只支持 Java 17+ 与 Spring Boot 3.x/4.x。需要 Spring Boot 2.x 或 JDK8 的既有项目实现时，使用 `java-microservice-dev` 的 Boot2/JDK8 模板，不要通过本生成器传入低版本参数。

## 生成契约

详细生成标准位于 `references/generation-contract.md`。当需要解释生成内容、修改 `assets/base-template`、调整 profile 裁剪、评估生成结果合规性，或用户追问具体规则时，读取该文件。

核心契约摘要：

- `minimal` 生成 `common + cms-api`；`standard` 生成 `common + cms-api + sdk-api`。
- 当用户明确要求 TCP 长连接、UDP 或 Netty 协议入口时，追加生成 `{projectName}-netty`。
- 所有可部署 API 模块都必须有统一响应、错误码、全局异常、trace/访问日志、健康检查、环境配置和 API 文档。

请求头、安全档位、签名、防重放和幂等的权威解释由 `java-backend-api-standard` 维护；本技能只保证生成模板引用这些字段和骨架。

- CMS 受保护接口使用 `authorization`、`x-udid`、`x-reqid`、`x-timestamp`、`x-sign`、`x-sign-alg`、`x-api-version`，不得要求 `x-api-key`。
- SDK 受保护接口使用 `x-api-key`、`x-udid`、`x-reqid`、`x-timestamp`、`x-sign`、`x-sign-alg`、`x-api-version`，并使用 `x-api-key + x-reqid` 防重放。
- 业务幂等必须基于业务字段，例如 `requestNo` 或 `businessNo`，不要生成 `idempotencyKey` 请求头。
- 复杂 SQL 通过 `src/main/resources/mapper/**/*.xml` 实现，Java Mapper 接口只保留方法签名和参数声明。
- Netty 模块必须复用 common 的统一返回码和日志契约，并提供 AUTH、HEARTBEAT、ACK、鉴权防篡改、handler dispatcher 和 TCP/UDP 基础入口。
- 生成模板中的默认开发管理员、固定签名密钥、内存限流、内存防重放和内存幂等都只是开发占位，生产必须替换。

## 边界

- 不要生成 MQ topic、Docker、Kubernetes、CI/CD 或生产级用户/角色/菜单/权限体系，除非用户明确要求。
- 不要生成默认 `core` 模块。只有当用户明确确认存在稳定共享业务能力，且该能力不属于单个 API 模块时，才新增独立业务库。
- 不要把 controller、service 实现、mapper、entity 或易变化的业务流程放入 `common`。
- 不要记录响应体、`authorization`、签名、密钥或原始 token。生成的访问日志通过在 controller 执行前包装和缓存请求来记录脱敏请求体。
- 将生成的默认开发管理员、固定签名密钥、固定 SDK 凭证、内存请求重放缓存和内存幂等实现视为开发占位实现。
- 将生成的内存限流、文件上传 content-type 检查、Actuator 暴露和 OpenAPI 开关视为生产评审点，而不是完整安全控制。
