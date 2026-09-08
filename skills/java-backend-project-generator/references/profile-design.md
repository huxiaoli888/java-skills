# 生成 Profile 设计

## 1. Profile 列表

| Profile | 状态 | 适用场景 | 输出重点 |
| --- | --- | --- | --- |
| `minimal` | 已支持，默认 | renren 风格轻量后台、小型内部管理系统、快速起步 | `common + cms-api`，优先形成后台管理闭环，保留统一响应、错误码、异常、trace、访问日志、CMS 安全骨架、健康检查和基础文档 |
| `standard` | 已支持，可选 | 需要 CMS/SDK 双入口、开放接口或公司级 API 规范增强的项目 | `common + cms-api + sdk-api`，在 minimal 基础上增加 SDK 入口、安全请求头、签名、防重放、审计扩展、限流、文件上传、可观测性、冒烟脚本和完整文档 |
| `standard + IncludeNetty` | 已支持，可选 | 需要 TCP 长连接、UDP 或 Netty 协议入口的项目 | 在 `standard` 基础上追加 `{projectName}-netty`，提供 TCP/UDP 启动框架、AUTH、HEARTBEAT、ACK、handler dispatcher、基础鉴权防篡改和日志 |

生产增强不是当前支持的 profile。需要上生产前强化时，按第 5 节路线图逐项实现运行时约束和测试，不要把路线图名称当成脚本参数。

## 2. 默认策略

默认使用 `minimal`，让不带参数的生成结果更接近 renren 的轻量后台框架，而不是一次性生成 CMS、SDK、Netty 和多套平台骨架。

只有用户明确要求“SDK 接口”“开放接口”“CMS + SDK 双入口”“standard profile”或指定 `-Profile standard` 时，才生成 `standard`。

只有用户明确要求 TCP 长连接、UDP、Netty 协议入口或传入 `-IncludeNetty` 时，才追加生成 `{projectName}-netty`。默认 `minimal` 和 `standard` 都不生成 Netty 模块。

## 3. Minimal 裁剪规则

`minimal` 当前不维护单独模板，而是从完整基线生成后裁剪；它的产品目标是轻量后台框架，后续应逐步向 renren 的后台管理闭环补齐：

- 删除 `{projectName}-sdk-api` 模块目录。
- 从根 `pom.xml` 删除 SDK module。
- 保留 `{projectName}-common` 和 `{projectName}-cms-api`。
- 保留 common 中的签名、请求追踪、CORS、SQL 注入防护、限流、文件上传安全等基础组件，避免破坏 CMS 安全契约和 checker 规则。
- `scripts/smoke-test.ps1 -Profile minimal` 只启动和验证 CMS API。
- README、模块地图、API 清单和冒烟说明改为 CMS-only 语义，避免生成项目文档仍承诺 SDK API。
- 当前已具备开发级 CMS 登录/token、`cms.sys` 用户/角色/菜单/权限/字典/参数查询、操作审计落库、操作日志查询和登录日志查询骨架；后续优先补齐生产级 RBAC 治理能力。
- 复杂安全能力、SDK 调用方管理、开放平台密钥、SDK 调用日志和 Netty 协议入口不得默认出现在 `minimal`。

## 4. Standard 输出规则

`standard` 是显式启用的增强脚手架：

- 生成 common、cms-api、sdk-api。
- CMS 受保护接口要求 `authorization`、`x-udid`、`x-reqid`、`x-timestamp`、`x-sign`、`x-sign-alg`、`x-api-version`。
- SDK 受保护接口要求 `x-api-key`、`x-udid`、`x-reqid`、`x-timestamp`、`x-sign`、`x-sign-alg`、`x-api-version`，并使用 `x-api-key + x-reqid` 防重放。
- 生成完整 smoke test，覆盖 CMS 和 SDK。

## 4.1 可选 Netty 输出规则

`-IncludeNetty` 是独立开关，不是新的 profile 名称。启用后：

- 在当前 profile 基础上追加 `{projectName}-netty` 模块。
- Netty 模块只依赖 `common`，不得依赖 `cms-api` 或 `sdk-api`。
- Netty 模块默认提供 TCP JSON 行帧入口和 UDP datagram JSON 入口。
- Netty 模块提供 AUTH、HEARTBEAT、统一 ACK/响应、`func + version` dispatcher、基础鉴权防篡改占位和 TCP/UDP 访问日志。
- Netty 模块中的固定 token、固定密钥、内存 replay 和内存限流都属于开发占位，生产必须替换。

## 5. 生产增强路线图

生产增强不应只是改文档。真正实现时必须增加运行时或测试约束：

当前阶段生产增强只作为路线图保留，不得传入生成器 `-Profile` 参数，也不得作为 `check_java_api_standard.py --profile` 参数。

- `application-prod.yml` 不允许固定 token、固定 secret、`changeme`、`dev-*` 等占位值。
- replay request store 必须替换为 Redis/JDBC 或等价组件。
- 限流必须替换为网关、Redis 或分布式限流。
- OpenAPI/Swagger UI 在生产默认关闭或受保护。
- Actuator 生产只暴露批准端点。
- 生产配置测试必须 fail-fast。

未完成这些约束前，不要把生产增强标为已支持 profile。

## 6. 验证矩阵

| Profile | 必跑验证 |
| --- | --- |
| `minimal` | 生成项目；确认无 sdk-api 模块；`mvn -q -DskipTests compile`；`check_java_api_standard.py --profile minimal --json --fail-on-error` |
| `standard` | 生成项目；确认 common/cms-api/sdk-api 都存在；`mvn -q -DskipTests compile`；CMS/SDK package；`check_java_api_standard.py --profile standard --json --fail-on-error` |
| `standard + IncludeNetty` | 生成项目；确认 common/cms-api/sdk-api/netty 都存在；`mvn -q -pl <projectName>-netty -am -DskipTests compile`；`check_java_api_standard.py --profile standard --json --fail-on-error` |

生产增强路线图待实现后，再新增正式 profile 名称和对应验证矩阵。
