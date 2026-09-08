# AGENTS.md

## 项目概况

`chaken-ai-test` 是 Java 17 / Spring Boot 4.0.5 Maven 多模块项目。

## 模块结构

| 模块 | 是否可部署 | 职责 |
| --- | --- | --- |
| chaken-ai-test-common | false | 统一响应、错误码、异常映射、trace 上下文、签名、防重放和幂等基础契约 |
| chaken-ai-test-cms-api | true | CMS/后台 HTTP API、CMS 业务服务和 CMS 自有持久化 |
| chaken-ai-test-sdk-api | true | 外部 SDK/开放平台 HTTP API、SDK 业务服务和 SDK 自有持久化 |

## 构建与运行

~~~bash
mvn -q -DskipTests compile
mvn spring-boot:run -pl <module>
~~~

## 编码规则

- 保持依赖方向单向。
- 不要把业务实现放入 common 模块。
- 不要让可部署 API 模块互相依赖。
- 数据库调用、mapper、repository、entity 和易变业务流程放在拥有接口的 API 模块中。
- 只有明确存在稳定跨 API 业务能力时，才新增独立共享业务模块。
- 公开 HTTP API 必须返回 `ApiResult<T>`，并保持 `reqid/code/message/ts/data`。
- SDK/开放平台 API 在实现敏感写操作前，必须先定义签名、防重放和业务键幂等。
- 新增模块前，先说明职责、上游、下游和验证方式。
