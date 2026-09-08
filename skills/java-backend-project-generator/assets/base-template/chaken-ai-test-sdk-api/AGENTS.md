# AGENTS.md

## 模块职责

`chaken-ai-test-sdk-api` 负责外部 SDK/开放平台 HTTP controller、SDK request/response DTO、签名验签适配器、防重放适配器、开放平台错误映射、配额/限流入口和业务键幂等入口。

## 是否可部署

True

## 禁止事项

- 不要加入 CMS/后台 API 契约。
- 不要在 controller 中直接加入数据库访问或核心业务规则。
- 不要定义公开 `idempotencyKey` 请求头或公共参数；使用 `requestNo`、`businessNo`、`orderNo` 等业务请求字段。
- 不要依赖 `chaken-ai-test-cms-api`。
- 不要引入循环依赖。

## 测试与运行

~~~bash
mvn test -pl chaken-ai-test-sdk-api -DskipTests=false
mvn clean package -pl chaken-ai-test-sdk-api -am -DskipTests
~~~
