# chaken-ai-test

`chaken-ai-test` 是 Java 17 / Spring Boot 4.0.5 / Maven 多模块后端项目骨架。

## 模块

| 模块 | 是否可部署 | 职责 |
| --- | --- | --- |
| `chaken-ai-test-common` | 否 | 统一响应、错误码、全局异常、trace、签名、防重放和幂等基础契约 |
| `chaken-ai-test-cms-api` | 是 | 后台/CMS HTTP API 入口、CMS 业务编排和 CMS 数据库访问 |
| `chaken-ai-test-sdk-api` | 是 | 对外 SDK / 开放平台 HTTP API 入口、SDK 业务编排和 SDK 数据库访问 |

## 依赖方向

```text
chaken-ai-test-cms-api  -> chaken-ai-test-common
chaken-ai-test-sdk-api  -> chaken-ai-test-common
```

可部署 API 模块之间不互相依赖。需要共享的稳定基础设施放入 `common`；业务编排、mapper、entity、repository 和数据库调用放入实际调用数据库的 API 模块。

## 构建

```bash
mvn -q -DskipTests compile
```

## 运行

```bash
mvn spring-boot:run -pl chaken-ai-test-cms-api -am
mvn spring-boot:run -pl chaken-ai-test-sdk-api -am
```

## 配置

CMS 和 SDK 模块都按环境拆分配置：

```text
application.yml
application-dev.yml
application-test.yml
application-prod.yml
```

配置项说明见 `docs/development/configuration_guide.md`。生产环境必须覆盖默认 `dev` profile，并替换 token、apiKey、secret、CORS 域名、内存请求重放缓存和内存幂等实现。
