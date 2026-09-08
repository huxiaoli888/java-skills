# AGENTS.md

## 模块职责

`chaken-ai-test-cms-api` 负责 CMS/后台 HTTP controller、CMS request/response DTO、开发级登录/token、后台认证/授权适配器、操作日志/登录日志查询和后台操作审计落库。

## 是否可部署

True

## 禁止事项

- 不要加入 SDK/开放平台 API 契约。
- 默认不要加入 SDK 应用、SDK 凭据或 SDK 调用日志管理包；只有明确需要开放平台后台管理时，才新增独立 CMS 大域。
- 不要在 controller 中直接加入数据库访问或核心业务规则。
- 不要依赖 `chaken-ai-test-sdk-api`。
- 不要引入循环依赖。

## 测试与运行

~~~bash
mvn test -pl chaken-ai-test-cms-api -DskipTests=false
mvn clean package -pl chaken-ai-test-cms-api -am -DskipTests
~~~
