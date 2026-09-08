# 接口冒烟测试

## 目的

`scripts/smoke-test.ps1` 用于验证 CMS API 和 SDK API 的最小可用链路：

- 构建聚合工程，默认执行 `mvn clean install`。
- 启动 CMS API 和 SDK API 两个可执行 jar。
- 等待 `/actuator/health` 返回 `UP`。
- 调用 CMS 分页接口并断言 `code=000000`。
- 调用 CMS 样例 CRUD 接口，依次完成创建、详情、修改、删除、分页并断言 `code=000000`。
- 使用 SDK 签名公参创建测试任务并断言 `code=000000`。
- 使用 SDK 签名公参查询刚创建的任务状态并断言 `code=000000`。
- 测试结束后自动停止本次脚本启动的 Java 进程。

## 运行

在项目根目录执行：

```powershell
.\scripts\smoke-test.ps1
```

如果已经完成构建，可以跳过构建：

```powershell
.\scripts\smoke-test.ps1 -SkipBuild
```

## 默认配置

| 项 | 默认值 |
| --- | --- |
| CMS 端口 | `18080` |
| SDK 端口 | `18081` |
| CMS 用户名 | `admin` |
| CMS 密码 | `admin123` |
| CMS `x-udid` | `cms-udid-001` |
| SDK `x-api-key` | `dev-sdk-api-key` |
| SDK secret | `dev-sdk-secret` |
| SDK `x-udid` | `sdk-udid-001` |

这些值仅用于开发环境。测试、预发和生产环境必须替换为环境专属配置。

## 注意事项

- 脚本启动前会检查 CMS/SDK 端口是否已占用；如果端口已占用，脚本会直接失败，不会停止非本脚本启动的服务。
- GET 签名使用规范化 query；SDK/CMS JSON 签名使用原始 body 参与 HMAC-SHA256；CMS form-urlencoded 表单签名使用原始 form body bytes，不再额外传输 body 摘要请求头。
- SDK 防重放键使用 `x-api-key + x-reqid`，`x-timestamp` 用于时间窗口校验；脚本每次请求都会生成新的 `x-reqid`。
- CMS API 和 SDK API 是两个独立进程，不能假设 CMS 能查询到 SDK 进程中创建的业务数据。
- CMS 操作日志/登录日志默认使用本模块数据库表；可选样例 CRUD 如果生成，则使用对应 API 模块内的 mapper、entity、XML 和迁移脚本说明分层方式。
