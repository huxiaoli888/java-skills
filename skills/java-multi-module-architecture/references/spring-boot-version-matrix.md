# Spring Boot 版本参考

## 新项目默认

- Java 17 或 21。
- Spring Boot 4.x。
- JUnit 5。
- 使用 `jakarta.*` 生态。

## 老项目默认

- 保持现有 Java/Spring Boot/Spring Cloud 版本。
- 不无故迁移 `javax.*` 到 `jakarta.*`。
- 不主动升级内部 starter、Nacos、Feign、MQ、MyBatis、数据库驱动。

## 常见版本线

| 技术线 | 推荐 JDK | 关键约束 |
| --- | --- | --- |
| Spring Boot 2.x | Java 8/11/17 | 仍使用 `javax.*` 生态 |
| Spring Boot 3.x | Java 17+ | 使用 `jakarta.*`，不支持 Java 8 |
| Spring Boot 4.x | Java 17+ | 使用 Spring Framework 7 / Jakarta 技术线，新项目默认 |
| Spring Cloud 2021.x | 常配 Boot 2.6/2.7 | 与 Boot 2.x 对齐 |
| Spring Cloud 2022.x/2023.x | Java 17+ | 与 Boot 3.x 对齐 |

## 主版本迁移前必须检查

- `javax.*` 到 `jakarta.*` 的影响。
- Spring Security、Validation、JPA、Servlet API 变化。
- Spring Cloud、Nacos、Feign、Gateway、MQ starter 兼容版本。
- 内部 starter 是否支持目标 Java 和 Spring Boot 主版本。
- 构建插件、编译参数、镜像基础包变化。
