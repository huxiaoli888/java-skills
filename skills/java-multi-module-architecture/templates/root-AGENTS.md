# AGENTS.md

## 项目概览

`{{projectName}}` 是基于 Java {{javaVersion}} / Spring Boot {{springBootVersion}} 的 Maven 多模块项目。

## 模块结构

| 模块 | 是否可部署 | 职责 | 上游 | 下游 |
| --- | --- | --- | --- | --- |
{{moduleTable}}

## 按需求定位模块

| 需求类型 | 优先修改模块 | 说明 |
| --- | --- | --- |
{{changeMap}}

## 构建与启动

```bash
mvn -q -DskipTests compile
mvn test -DskipTests=false
mvn spring-boot:run -pl <module>
```

## 编码规则

- 遵守单向依赖，不新增循环依赖。
- 不把业务实现放入 common。
- controller 只处理 HTTP 入参、校验和响应适配。
- service 或 core 承担业务编排和规则。
- 新增模块前先说明职责、上下游、是否可部署和验证命令。
