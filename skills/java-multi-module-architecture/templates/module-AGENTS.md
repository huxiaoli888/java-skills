# AGENTS.md

## 模块职责

`{{moduleName}}` 负责 {{modulePurpose}}。

## 是否可部署

{{deployable}}

## 拥有的入口

{{entries}}

## 下游依赖

{{dependencies}}

## 本模块不要放

{{forbidden}}

## 测试与启动

```bash
mvn test -pl {{moduleName}} -DskipTests=false
mvn clean package -pl {{moduleName}} -am -DskipTests
```
