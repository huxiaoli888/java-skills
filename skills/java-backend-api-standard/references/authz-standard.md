# CMS 鉴权、授权与数据权限标准




## 目录

- [1. 目标](#1-目标)
- [2. 认证与授权边界](#2-认证与授权边界)
- [3. 推荐权限模型](#3-推荐权限模型)
- [4. 权限注解标准组件](#4-权限注解标准组件)
- [5. 数据权限](#5-数据权限)
- [6. 多租户与开放平台调用方](#6-多租户与开放平台调用方)
- [7. 操作审计](#7-操作审计)
- [8. 上线前验证](#8-上线前验证)

## 1. 目标

本标准用于后台 CMS/API 模块的登录态、权限码、角色、菜单和数据权限设计。CMS 接口不使用 `x-api-key` 作为后台公参，请求唯一编号由 `x-reqid` 表达，后台登录态由 `authorization: Bearer <token>` 表达，设备或用户唯一标识由 `x-udid` 表达，受保护接口同时要求 `x-timestamp` 时间窗口校验、`x-sign` 防篡改签名、`x-sign-alg` 签名算法和 `x-api-version` 契约版本。

## 2. 认证与授权边界

认证回答：

```text
当前请求是谁？
```

授权回答：

```text
当前用户能否执行这个操作或访问这份数据？
```

规则：

- `auth-exclude-paths` 只配置登录、验证码、探活等公开入口；这些接口不需要 token 或签名认证，也不具备 `x-udid`。
- `udid-exclude-paths` 只跳过 `x-udid` 前置校验，不代表跳过 token 或 `x-sign` 验签。
- 受保护接口必须先有认证身份，再做权限和数据范围判断。
- 不能只靠前端菜单隐藏实现权限。

## 3. 推荐权限模型

基础模型：

```text
User
Role
Permission
Menu
UserRole
RolePermission
RoleMenu
```

权限码推荐：

```text
system:user:create
system:user:update
system:user:delete
system:user:page
system:role:grant
sdk:app:create
sdk:app:disable
```

规则：

- 权限码是稳定契约，不随页面中文名变化。
- Controller 或 application service 入口声明权限要求。
- 菜单权限和接口权限可以关联，但接口权限必须由服务端独立校验。
- 超级管理员也应经过统一授权组件，只是策略返回允许。

## 4. 权限注解标准组件

推荐接口：

```java
@RequirePermission("system:user:create")
public ApiResult<UserResponse> create(@Valid @RequestBody CreateUserRequest request) {
    return ApiResult.success(userService.create(request));
}
```

推荐注解：

```java
@Target({ElementType.METHOD, ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
public @interface RequirePermission {
    String[] value();
    boolean any() default false;
}
```

规则：

- 缺少登录态返回 `AC0002`。
- 已登录但无权限返回 `AC0003`。
- 权限失败不得返回“资源不存在”来掩盖鉴权问题，除非接口契约明确要求防枚举。
- 实现中应包含 `RequirePermission`、`PermissionEvaluator`、`PermissionAuthorizationAspect`、`PrincipalContext` 和 `AuthenticatedPrincipal`。
- CMS Filter 只负责认证、`x-udid` 前置校验、`x-sign` 验签和写入当前主体上下文；真实 RBAC、ABAC、SSO 或统一权限中心通过替换 `PermissionEvaluator` 接入。

## 5. 数据权限

常见数据范围：

```text
全部数据
本部门及下级
本部门
本人
自定义组织范围
```

规则：

- 数据权限条件由服务端根据当前用户、角色、组织生成。
- 前端传入的部门、租户、用户范围只能作为查询条件，不能作为授权依据。
- Mapper 动态 SQL 中的数据权限字段必须使用白名单。
- 导出接口必须应用与查询接口相同或更严格的数据权限。
- 实现中应提供 `TenantContext`、`DataPermissionScope` 和 `DataPermissionContext`，业务 Mapper 或查询服务只能读取服务端生成的数据权限范围。

## 6. 多租户与开放平台调用方

如果系统存在租户：

- `tenantId` 必须来自登录态、token、网关上下文或已认证调用方。
- 不信任客户端 body/query 中的 `tenantId`。
- 数据库查询必须强制带租户条件，公共字典等例外表需白名单。

如果 SDK/OpenAPI 代表外部调用方：

- `x-api-key` 解析出的调用方身份应映射到租户、应用或商户。
- 该规则仅适用于 SDK/OpenAPI/第三方调用方，不适用于 CMS 后台接口公参；CMS 后台仍使用登录主体、`authorization` 和 `x-udid` 表达调用身份。
- 调用方禁用、过期、密钥轮换必须立即生效或按缓存 TTL 生效。
- 高风险接口应增加 IP 白名单、mTLS 或风控策略。

## 7. 操作审计

必须审计：

- 新增、修改、删除、导入、导出。
- 用户、角色、权限、菜单、密钥和配置变更。
- 支付、订单、退款、回调和状态流转。

审计字段至少包含：

```text
operator, operationType, businessId, success, failureCode, reqid, traceId, clientIp, durationMs, createdTime
```

## 8. 上线前验证

- 所有受保护 CMS 接口都有认证。
- 敏感接口有权限码或等价授权规则。
- 查询、详情、导出接口已应用数据权限。
- `auth-exclude-paths` 和 `udid-exclude-paths` 最小化。
- 权限失败、未登录、数据越权都有测试。
