# AGENTS.md

## 模块职责

`chaken-ai-test-common` 负责稳定共享基础设施契约：`ApiResult`、`PageResult`、错误码抽象、全局异常映射、trace 上下文、签名辅助、防重放接口、幂等接口、校验支持、常量和纯工具类。

## 是否可部署

False

## 禁止事项

- 不要加入 controller、service 实现、mapper、entity、MQ consumer、scheduler 或易变业务流程。
- 不要加入仅 CMS 或仅 SDK 使用的 request/response DTO。
- 不要引入循环依赖。

## 测试与运行

~~~bash
mvn test -pl chaken-ai-test-common -DskipTests=false
mvn clean package -pl chaken-ai-test-common -am -DskipTests
~~~
