# 多模块迁移阶段

## 阶段 0：现状盘点

目标：确认当前结构和风险，不改代码。

- 父 POM、模块、包结构、启动类、配置文件清单。
- controller、service、mapper、listener、client、job 入口清单。
- 跨包调用、数据库访问、MQ、Redis、外部系统依赖清单。
- 当前测试和构建命令。

验证：

```bash
mvn clean package -DskipTests
mvn dependency:tree
```

## 阶段 1：抽稳定契约

目标：只抽稳定共享内容到 `common`、`contract` 或 `client`。

允许移动：

- 常量、错误码、枚举。
- 稳定 DTO。
- 配置属性类。
- Feign/client 接口契约。
- 纯工具类。

禁止移动：

- controller。
- service 实现。
- mapper/dao。
- MQ consumer。
- 外部系统实现类。

## 阶段 2：拆入口模块

目标：按调用方拆 API/SDK/service/protocol 入口。

必须保证：

- API 路径、字段、错误码兼容。
- 协议 handler 保持报文兼容。
- controller 只做入参校验和调用 service。

## 阶段 3：拆异步与外部集成

目标：把 MQ 消费、补偿、外部系统适配拆到独立边界。

必须保证：

- topic、group、tag、payload 兼容。
- 幂等键、重试、补偿策略明确。
- 外部调用有超时、降级和脱敏日志。

## 阶段 4：部署与文档同步

目标：让新模块可构建、可部署、可回滚、可维护。

- 更新父 POM modules。
- 写清每个可部署模块启动命令。
- 说明配置、端口、profile、环境变量。
- 更新根和模块 `AGENTS.md`。
- 更新架构图、依赖矩阵、测试说明。
