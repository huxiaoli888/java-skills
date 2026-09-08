# CMS 鉴权、授权与数据权限标准

## 认证与授权

CMS 接口不使用 `x-api-key` 作为后台公参。后台身份由以下字段表达：

```text
authorization: Bearer <token>
x-udid
x-reqid
x-timestamp
x-sign
x-sign-alg
x-api-version
```

规则：

- `auth-exclude-paths` 只配置登录、验证码、探活等公开入口。
- `udid-exclude-paths` 只跳过 `x-udid` 前置校验，不代表跳过认证、`x-timestamp` 时间窗口或 `x-sign` 验签。
- 受保护接口必须先有认证身份，再做权限和数据范围判断。
- 不能只靠前端菜单隐藏实现权限。

## 权限模型

推荐模型：

```text
User
Role
Permission
Menu
UserRole
RolePermission
RoleMenu
```

权限码示例：

```text
system:user:create
system:user:update
system:user:delete
system:user:page
sdk:app:create
sdk:app:disable
```

权限码是稳定契约，不随页面中文名变化。菜单权限和接口权限可以关联，但接口权限必须由服务端独立校验。

## 权限注解

推荐形式：

```java
@RequirePermission("system:user:create")
```

约定：

- 缺少登录态返回 `AC0002`。
- 已登录但无权限返回 `AC0003`。
- 权限失败不得被前端隐藏逻辑替代。

## 数据权限

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
- 导出接口必须应用与查询接口相同或更严格的数据权限。

## 多租户和 SDK 调用方

- `tenantId` 必须来自登录态、token、网关上下文或已认证调用方。
- SDK/OpenAPI 的 `x-api-key` 解析结果应映射到租户、应用或商户。
- 调用方禁用、过期、密钥轮换必须立即生效或按缓存 TTL 生效。

## 上线前验证

- 所有受保护 CMS 接口都有认证。
- 敏感接口有权限码或等价授权规则。
- 查询、详情、导出接口已应用数据权限。
- `auth-exclude-paths` 和 `udid-exclude-paths` 最小化。
