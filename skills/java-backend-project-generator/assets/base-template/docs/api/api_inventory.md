# 接口清单与模块归属

## 1. 文档目标

本文用于在生成 controller、request DTO、response DTO 和 service 之前，先固定 `chaken-ai-test` 的接口边界。

当前业务假设：

- `chaken-ai-test-cms-api` 面向后台管理人员、运营人员和内部管理员。
- `chaken-ai-test-sdk-api` 面向外部系统、SDK 调用方、H5 或其他客户端。
- 业务暂按“AI 测试任务、测试结果、后台样例 CRUD、回调通知”建模。后续如果实际业务不同，优先调整本文，再生成代码。

表中 URL 是模块内路径。实际访问路径还需要拼接模块 context path：

```text
CMS: /chaken-ai-test-cms-api + URL
SDK: /chaken-ai-test-sdk-api + URL
```

## 2. 模块归属规则

| 模块 | 使用主体 | 放什么 | 不放什么 |
| --- | --- | --- | --- |
| `chaken-ai-test-cms-api` | 后台管理端 | CMS controller、CMS request/response DTO、开发级登录/token、后台认证鉴权适配、操作日志/登录日志查询、后台操作审计落库、CMS 业务 service、CMS mapper/entity/repository | SDK 对外契约、签名验签细节、默认 SDK 调用方管理 |
| `chaken-ai-test-sdk-api` | 外部系统、SDK、H5、客户端 | SDK controller、SDK request/response DTO、签名验签入口、防重放入口、开放平台错误映射、SDK 业务 service、SDK mapper/entity/repository | CMS 管理接口、后台 DTO |
| `chaken-ai-test-common` | 所有模块 | `ApiResult`、`PageResult`、错误码、异常、trace、安全接口、纯工具 | controller、service 实现、mapper、entity、易变业务流程 |

依赖方向：

```text
cms-api -> common
sdk-api -> common
```

可部署 API 模块之间不得互相依赖。
数据库调用、mapper、entity、repository 和事务边界放在实际调用数据库的 API 模块中。

## 3. 统一接口契约

### 3.1 响应报文

所有 HTTP JSON 接口统一返回：

```json
{
  "reqid": "client-generated-x-reqid",
  "code": "000000",
  "message": "成功",
  "ts": 1716000000000,
  "data": {}
}
```

规则：

- 成功码固定为 `000000`。
- 失败码使用 6 位字符串 `SMEEEE`，公共错误码使用 `AC0001` 到 `AC9999`。
- 请求唯一编号通过 `x-reqid` 请求头传入；服务端将同一个值写入响应 JSON 的 `reqid`。
- `traceId` 只进入日志和内部链路，不放入公开 JSON 响应体。
- Controller 返回 `ApiResult<T>`，不直接返回 `Map`、entity 或裸 DTO。

### 3.2 通用请求头

所有 API：

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

SDK/开放平台/敏感写接口额外要求：

```text
x-api-key
```

规则：

- 请求头全部小写。
- `authorization` 主要承载登录后的 token 或 Bearer token；`x-udid` 表示登录或鉴权后的设备/用户唯一标识；签名结果统一放在 `x-sign`，不放在 `authorization`。
- `x-udid` 不是登录前天然存在的字段；登录、验证码、探活等公开接口必须配置到 `auth-exclude-paths`，不能只放入 `udid-exclude-paths`。
- 未命中排除配置的接口先校验 `x-udid`，为空直接返回统一错误，非空后再进入原有 token 或签名鉴权。
- 不定义 `idempotencyKey` 公参或请求头。幂等由业务报文中的 `requestNo`、`businessNo`、`taskNo` 等业务唯一键表达。
- GET 签名使用规范化 query；POST JSON 签名使用 HTTP 原始 body 字节，不使用反序列化后的 Java 对象；CMS POST `application/x-www-form-urlencoded` 表单签名使用 HTTP 原始 form body bytes。

## 4. CMS 接口清单

### 4.1 P0 接口

| ID | 接口名称 | Method | URL | 使用主体 | 认证 | 签名 | 防重放 | 幂等 | Request DTO | Response DTO | Service 方法 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CMS-AUTH-001 | 后台登录 | POST | `/api/v1/cms/auth/login` | 后台管理员 | 无 | 否 | 否 | 否 | `CmsLoginRequest` | `CmsLoginResponse` | `CmsAuthService.login` | 校验用户名密码，生成 Bearer token，并写入登录日志 |
| CMS-AUTH-002 | 后台登出 | POST | `/api/v1/cms/auth/logout` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 否 | 无 | `Void` | `CmsAuthService.logout` | 注销当前 token，并写入登录日志 |
| CMS-SYS-001 | 查询当前后台用户 | GET | `/api/v1/cms/sys/current-user` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 否 | 无 | `SysCurrentUserResponse` | `SysUserService.currentUser` | 返回当前用户、角色、权限和菜单 |
| CMS-SYS-002 | 分页查询后台用户 | GET | `/api/v1/cms/sys/users` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 否 | `SysUserPageQuery` | `PageResult<SysUserResponse>` | `SysUserService.page` | 开发级用户查询骨架 |
| CMS-SYS-003 | 查询后台角色 | GET | `/api/v1/cms/sys/roles` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 否 | 无 | `List<SysRoleResponse>` | `SysRoleService.listActiveRoles` | 开发级角色查询骨架 |
| CMS-SYS-004 | 查询后台菜单 | GET | `/api/v1/cms/sys/menus` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 否 | 无 | `List<SysMenuResponse>` | `SysMenuService.listActiveMenus` | 开发级菜单和权限查询骨架 |
| CMS-SYS-005 | 分页查询后台字典 | GET | `/api/v1/cms/sys/dicts` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 否 | `SysDictPageQuery` | `PageResult<SysDictResponse>` | `SysDictService.page` | 开发级字典查询骨架 |
| CMS-SYS-006 | 查询字典项 | GET | `/api/v1/cms/sys/dicts/{dictCode}/items` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 否 | 无 | `List<SysDictItemResponse>` | `SysDictService.listItems` | 开发级字典项查询骨架 |
| CMS-SYS-007 | 分页查询后台参数 | GET | `/api/v1/cms/sys/params` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 否 | `SysParamPageQuery` | `PageResult<SysParamResponse>` | `SysParamService.page` | 开发级参数查询骨架，不保存密钥类配置 |
| CMS-TASK-001 | 分页查询测试任务 | GET | `/api/v1/cms/test-tasks` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 否 | `TestTaskPageQuery` | `PageResult<TestTaskResponse>` | `TestTaskQueryService.pageTasks` | 支持按应用、状态、时间范围查询 |
| CMS-TASK-002 | 查询测试任务详情 | GET | `/api/v1/cms/test-tasks/{taskNo}` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 否 | 无 | `TestTaskDetailResponse` | `TestTaskQueryService.getTaskDetail` | 返回任务、请求摘要、执行结果摘要 |
| CMS-SAMPLE-001 | 分页查询样例条目 | GET | `/api/v1/cms/sample-items` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 否 | `SampleItemPageQuery` | `PageResult<SampleItemResponse>` | `SampleItemService.pageItems` | 简单 CRUD 样例的分页查询 |
| CMS-SAMPLE-002 | 创建样例条目 | POST | `/api/v1/cms/sample-items` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 业务可选 | `SampleItemCreateRequest` | `SampleItemDetailResponse` | `SampleItemService.createItem` | 简单 CRUD 样例的新增接口，记录操作审计 |
| CMS-SAMPLE-003 | 查询样例条目详情 | GET | `/api/v1/cms/sample-items/{itemId}` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 否 | 无 | `SampleItemDetailResponse` | `SampleItemService.getItem` | 简单 CRUD 样例的详情接口 |
| CMS-SAMPLE-004 | 修改样例条目 | PUT | `/api/v1/cms/sample-items/{itemId}` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 业务可选 | `SampleItemUpdateRequest` | `SampleItemDetailResponse` | `SampleItemService.updateItem` | 简单 CRUD 样例的修改接口，记录操作审计 |
| CMS-SAMPLE-005 | 删除样例条目 | DELETE | `/api/v1/cms/sample-items/{itemId}` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 业务可选 | 无 | `Void` | `SampleItemService.deleteItem` | 简单 CRUD 样例的删除接口，记录操作审计 |
| CMS-RESULT-001 | 查询任务结果详情 | GET | `/api/v1/cms/test-tasks/{taskNo}/result` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 否 | 无 | `TestResultResponse` | `TestResultQueryService.getResult` | 展示 AI 测试结果，不返回敏感原始凭证 |
| CMS-LOG-001 | 分页查询操作日志 | GET | `/api/v1/cms/logs/operations` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 否 | `OperationLogPageQuery` | `PageResult<OperationLogResponse>` | `OperationLogService.page` | 用于追踪后台操作 |
| CMS-LOG-002 | 分页查询登录日志 | GET | `/api/v1/cms/logs/logins` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 否 | `LoginLogPageQuery` | `PageResult<LoginLogResponse>` | `LoginLogService.page` | 用于追踪后台登录/退出 |

### 4.2 P1 候选接口

| ID | 接口名称 | Method | URL | 使用主体 | 认证 | 签名 | 防重放 | 幂等 | Request DTO | Response DTO | Service 方法 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CMS-CONFIG-001 | 查询系统配置 | GET | `/api/v1/cms/configs` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 否 | `SystemConfigQuery` | `List<SystemConfigResponse>` | `SystemConfigService.listConfigs` | 后续如引入配置中心可调整 |
| CMS-CONFIG-002 | 更新系统配置 | PUT | `/api/v1/cms/configs/{configKey}` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 业务可选 | `UpdateSystemConfigRequest` | `SystemConfigResponse` | `SystemConfigService.updateConfig` | 必须记录变更前后摘要 |

### 4.3 可选开放平台管理接口

以下接口不属于默认 CMS 骨架。只有明确需要后台管理 SDK 调用方、密钥或调用记录时，才新增到 CMS 模块的独立大域，例如 `cms.openapi` 或 `cms.sdkmanage`。

| ID | 接口名称 | Method | URL | 使用主体 | 认证 | 签名 | 防重放 | 幂等 | Request DTO | Response DTO | Service 方法 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CMS-OPENAPI-001 | 分页查询调用方应用 | GET | `/api/v1/cms/openapi/apps` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 否 | `AppPageQuery` | `PageResult<AppResponse>` | `OpenApiAppManageService.pageApps` | 查询 SDK 调用方应用 |
| CMS-OPENAPI-002 | 创建调用方应用 | POST | `/api/v1/cms/openapi/apps` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 业务可选 | `CreateAppRequest` | `AppResponse` | `OpenApiAppManageService.createApp` | 创建 `x-api-key` 对应应用；secret 只在创建时返回或按策略展示 |
| CMS-OPENAPI-003 | 修改调用方应用 | PUT | `/api/v1/cms/openapi/apps/{appId}` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 业务可选 | `UpdateAppRequest` | `AppResponse` | `OpenApiAppManageService.updateApp` | 修改名称、状态、限流档位等 |
| CMS-OPENAPI-004 | 禁用/启用调用方应用 | POST | `/api/v1/cms/openapi/apps/{appId}/status` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 业务可选 | `UpdateAppStatusRequest` | `AppResponse` | `OpenApiAppManageService.updateAppStatus` | 状态变更必须记录操作审计 |
| CMS-OPENAPI-005 | 重置应用密钥 | POST | `/api/v1/cms/openapi/apps/{appId}/secret/reset` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 操作流水号 | `ResetAppSecretRequest` | `ResetAppSecretResponse` | `OpenApiAppSecretService.resetSecret` | 高敏操作，需要二次确认和审计 |
| CMS-OPENAPI-006 | 分页查询 SDK 调用记录 | GET | `/api/v1/cms/openapi/sdk-call-logs` | 后台管理员 | Bearer token + x-udid | 是 | 是 | 否 | `SdkCallLogPageQuery` | `PageResult<SdkCallLogResponse>` | `SdkCallLogQueryService.pageLogs` | 用于排查外部调用问题 |

## 5. SDK 接口清单

### 5.1 P0 接口

| ID | 接口名称 | Method | URL | 使用主体 | 认证 | 签名 | 防重放 | 幂等 | Request DTO | Response DTO | Service 方法 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SDK-TASK-001 | 创建 AI 测试任务 | POST | `/api/v1/sdk/test-tasks` | 外部系统/SDK | `x-api-key` | 是 | 是 | `requestNo` 或 `businessNo` | `CreateTestTaskRequest` | `CreateTestTaskResponse` | `TestTaskService.createTask` | 敏感写接口，必须验签、防重放、业务幂等 |
| SDK-TASK-002 | 查询任务状态 | GET | `/api/v1/sdk/test-tasks/{taskNo}` | 外部系统/SDK | `x-api-key` | 是 | 可选 | 否 | 无 | `TestTaskStatusResponse` | `TestTaskService.getTaskStatus` | 查询类接口可不做幂等 |
| SDK-RESULT-001 | 查询测试结果 | GET | `/api/v1/sdk/test-tasks/{taskNo}/result` | 外部系统/SDK | `x-api-key` | 是 | 可选 | 否 | 无 | `TestResultResponse` | `TestResultQueryService.getResultForSdk` | 只返回调用方有权访问的数据 |
| SDK-TASK-003 | 取消测试任务 | POST | `/api/v1/sdk/test-tasks/{taskNo}/cancel` | 外部系统/SDK | `x-api-key` | 是 | 是 | `requestNo` | `CancelTestTaskRequest` | `CancelTestTaskResponse` | `TestTaskService.cancelTask` | 状态变更接口，必须校验状态机 |
| SDK-CALLBACK-001 | 接收外部测试结果回调 | POST | `/api/v1/sdk/callbacks/test-results` | 外部系统/合作方 | `x-api-key` | 是 | 是 | `callbackNo` 或 `businessNo` | `TestResultCallbackRequest` | `CallbackAckResponse` | `TestResultCallbackService.receiveResult` | 状态变更前必须验签；重复回调返回原始处理结果 |

### 5.2 P1 候选接口

| ID | 接口名称 | Method | URL | 使用主体 | 认证 | 签名 | 防重放 | 幂等 | Request DTO | Response DTO | Service 方法 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SDK-APP-001 | 查询当前应用信息 | GET | `/api/v1/sdk/apps/current` | 外部系统/SDK | `x-api-key` + `x-sign` | 是 | 可选 | 否 | 无 | `CurrentAppResponse` | `SdkAppQueryService.getCurrentApp` | 便于 SDK 自检；登录后 token 可通过 `authorization` 传入 |
| SDK-CALL-001 | 上报 SDK 客户端事件 | POST | `/api/v1/sdk/client-events` | 外部系统/SDK | `x-api-key` + `x-sign` | 是 | 是 | `eventNo` | `CreateClientEventRequest` | `CreateClientEventResponse` | `ClientEventService.createEvent` | 用于 SDK 侧埋点或诊断；登录后 token 可通过 `authorization` 传入 |
| SDK-HEALTH-001 | SDK 服务探活 | GET | `/api/v1/sdk/health` | 外部系统/SDK | 可选 | 否 | 否 | 否 | 无 | `HealthResponse` | 无或 `HealthQueryService.health` | 只返回服务可用性，不返回内部配置 |

## 6. DTO 命名与包归属

CMS DTO 建议路径：

```text
chaken-ai-test-cms-api
  src/main/java/com/chaken/ai/test/cms/{large-domain}/controller
  src/main/java/com/chaken/ai/test/cms/{large-domain}/dto/request
  src/main/java/com/chaken/ai/test/cms/{large-domain}/dto/response
```

SDK DTO 建议路径：

```text
chaken-ai-test-sdk-api
  src/main/java/com/chaken/ai/test/sdk/{domain}/controller
  src/main/java/com/chaken/ai/test/sdk/{domain}/dto/request
  src/main/java/com/chaken/ai/test/sdk/{domain}/dto/response
```

API 模块内 service 建议路径：

```text
chaken-ai-test-cms-api
  src/main/java/com/chaken/ai/test/cms/{large-domain}/service
  src/main/java/com/chaken/ai/test/cms/{large-domain}/model
  src/main/java/com/chaken/ai/test/cms/{large-domain}/repository

chaken-ai-test-sdk-api
  src/main/java/com/chaken/ai/test/sdk/{domain}/service
  src/main/java/com/chaken/ai/test/sdk/{domain}/repository
```

规则：

- Request DTO 和 response DTO 不复用为 entity。
- CMS DTO 不与 SDK DTO 复用，除非确认为稳定公共契约。
- 普通 CMS CRUD 和默认 SDK 示例可以直接由 service 接收本模块 request DTO；交易接口或复杂业务可以在模块内按需新增 command/query。不要让 CMS DTO 与 SDK DTO 互相依赖。
- CMS 包按大业务域组织。账号、角色、菜单、权限、部门、参数、字典等后台系统能力统一归入 `cms.sys`；订单类、系统类、开放平台管理类等才作为独立大域。
- request DTO 与 response DTO 默认分开。只有字段含义、校验规则、展示规则和生命周期完全一致时，才允许复用轻量 DTO。

## 7. 首批代码生成建议

建议第一批只生成 P0 的最小代码骨架：

1. `SDK-TASK-001` 创建 AI 测试任务。
2. `SDK-TASK-002` 查询任务状态。
3. `CMS-TASK-001` 分页查询测试任务。
4. `CMS-TASK-002` 查询测试任务详情。

原因：

- 这 4 个接口覆盖 SDK 写入、SDK 查询、CMS 查询三条主路径。
- 可以先验证统一响应、DTO、controller/service 分层、签名入口、防重放和业务幂等位置。
- 暂不生成应用密钥重置、系统配置、调用日志等外围接口，避免在业务未确认前过度实现。
- 暂不生成 SDK 调用方应用管理、SDK 密钥管理、SDK 调用日志查询等 CMS 侧开放平台管理包，避免 CMS 默认框架混入 SDK 管理语义。

## 8. 待确认问题

- AI 测试任务的真实业务字段是什么，例如模型、测试集、提示词、评测指标、回调地址等。
- CMS 登录鉴权使用 Spring Security、Sa-Token、Shiro 还是已有统一认证。
- SDK 签名算法是否固定 `HMAC-SHA256`。
- `x-api-key` 与 secret 的存储位置是数据库、配置中心还是外部开放平台。
- 任务结果是同步生成、异步生成，还是依赖外部 AI 服务回调。

## 9. 实现状态

已生成 P0 最小代码骨架：

| ID | 状态 | 说明 |
| --- | --- | --- |
| `SDK-TASK-001` | 已生成骨架 | 已生成 SDK controller、request DTO、response DTO、SDK 模块内轻量 service 接口和占位实现 |
| `SDK-TASK-002` | 已生成骨架 | 已生成 SDK controller、response DTO、SDK 模块内轻量 service 接口和占位实现 |
| `CMS-TASK-001` | 已生成骨架 | 已生成 CMS controller、query DTO、response DTO、CMS 模块内 query service 接口和占位实现 |
| `CMS-TASK-002` | 已生成骨架 | 已生成 CMS controller、response DTO、CMS 模块内 query service 接口和占位实现 |
| `CMS-AUTH-001` 到 `CMS-AUTH-002` | 已生成开发级实现 | 已生成登录、登出、PBKDF2 密码校验、数据库 token、登录日志和 Bearer token 校验 |
| `CMS-SYS-001` 到 `CMS-SYS-007` | 已生成查询骨架 | 已生成当前用户、用户、角色、菜单、字典、字典项、参数查询接口、mapper、entity 和 Mapper XML |
| `CMS-LOG-001` 到 `CMS-LOG-002` | 已生成查询骨架 | 已生成操作日志和登录日志查询接口、mapper、entity 和 Mapper XML |
| `CMS-SAMPLE-001` 到 `CMS-SAMPLE-005` | 已生成样例 | 已生成 CMS 简单 CRUD 样例，覆盖 create/page/detail/update/delete、DTO、CMS 单 service 和内存实现 |

仍需生产替换或按业务补齐：

- CMS 当前是开发级登录、token、角色、权限和菜单骨架；生产环境需要替换默认管理员、密码策略、权限码治理、数据权限和租户策略。
- 生产级 SDK 密钥解析。当前只有基于配置的骨架实现。
- 生产级请求重放存储。当前只有内存骨架实现，重启会丢失。
- 业务幂等存储。
- 业务表 repository/mapper/entity 需要按真实业务补齐；CMS 登录、系统管理、操作日志、登录日志已有开发级 mapper/entity/XML。
- 复杂 SQL 参考 renren 项目通过 Mapper XML 实现，不在 Mapper 注解或 service 中拼接长 SQL。
- 更完整的 MockMvc、mapper 集成测试和真实数据库测试。

已生成安全骨架：

- common 复用型 query/body/form 签名鉴权支持。
- CMS `CmsSecurityFilter`，支持 Bearer token + `x-udid` + `x-timestamp` 时间窗口 + `x-sign` 防篡改签名 + `x-sign-alg`/`x-api-version`。
- CMS/SDK 均支持 `auth-exclude-paths` 和 `udid-exclude-paths` 配置；未排除接口先校验 `x-udid`。
- 全局访问日志记录脱敏后的请求体、请求时间、返回时间、响应 `code/message`。
- common 按 `common.log.annotation/model/service/aspect` 提供 `OperationAudit` 注解、审计记录、审计服务接口、日志型默认实现和 AOP 切面；CMS 模块提供 DB 审计实现、操作日志查询和登录日志查询。
- common 提供 `ApiCorsConfiguration` 和 `ApiCorsProperties`，通过 `chaken.web.cors` 统一配置浏览器跨域，生产环境必须替换为明确来源。
- common 提供 `SqlInjectionGuard` 和 `SqlInjectionFilter`，对 query string 和可选 form 参数做轻量 SQL 注入风险拦截；Mapper 仍必须使用参数绑定和白名单。
- SDK `SdkSecurityFilter`，在单个 filter 内完成请求体缓存、GET query/POST JSON 签名验签、时间戳窗口校验和防重放。
- SDK 配置化测试 `apiKey/secret` 解析器。
