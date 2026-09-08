# Forward-test 场景

本文件用于维护 `java-backend-development-orchestrator` 后做行为验证。普通 Java/Netty 任务不需要默认读取。

## 场景一：只改已有接口实现

输入任务：

```text
在已有 Spring Boot 项目里给订单查询接口增加一个过滤条件，并补测试。
```

预期关注点：

- Lead skill 选择 `java-microservice-dev`。
- Supporting skill 只在需要时选择 `java-backend-api-standard` 和 `java-development-principles`。
- 不应加载项目生成器、事故修复或 Netty skill。
- 输出实现前说明和最小验证命令。

### Input Sample

```text
GET /api/v1/orders?status=PAID 需要新增 channel 过滤条件。
```

### Expected Findings

- rule: 具体已有接口实现应选择 `java-microservice-dev`。
  keyword: `java-microservice-dev`
- rule: API 契约和开发原则只作为必要 supporting skill。
  keyword: Supporting skill
- rule: 不应路由到脚手架、事故或 Netty。
  keyword: 不应加载项目生成器

## 场景二：Netty WebSocket 协议设计

输入任务：

```text
把原 TCP 长连接扩展为 Netty WebSocket，要求统一响应、ACK、心跳和防重放。
```

预期关注点：

- Lead skill 选择 `netty-handler-dispatcher`。
- Supporting skill 选择 `java-backend-api-standard` 处理通用响应和错误码。
- 不应使用 `java-microservice-dev` 直接生成业务代码。
- 输出协议边界、handler 分发和验证计划。

### Input Sample

```text
现有 TCP func=AUTH/HEARTBEAT，需要新增 WebSocket 连接入口。
```

### Expected Findings

- rule: Netty WebSocket 协议设计应选择 `netty-handler-dispatcher`。
  keyword: `netty-handler-dispatcher`
- rule: 通用响应和错误码由 `java-backend-api-standard` 支撑。
  keyword: `java-backend-api-standard`
- rule: 输出协议边界、handler 分发和验证计划。
  keyword: handler 分发

## 场景三：线上 500 激增

输入任务：

```text
刚发布后后台接口 500 激增，要求马上处理。
```

预期关注点：

- Lead skill 选择 `java-incident-fix`。
- 先给止血选项，再说明证据采集和回滚/热修决策。
- 热修后才使用 `java-code-review` 做回归风险复核。
- 不应先做架构重构或脚手架生成。

### Input Sample

```text
发布 10 分钟后 /cms/order/page 500 从 0.1% 升到 18%。
```

### Expected Findings

- rule: 线上 500 激增应优先选择 `java-incident-fix`。
  keyword: `java-incident-fix`
- rule: 先止血，再证据采集和回滚/热修决策。
  keyword: 止血
- rule: 不应先做架构重构或脚手架生成。
  keyword: 脚手架生成

## 场景四：补齐 AI 编程知识库

输入任务：

```text
帮我给这个 Java 多模块项目生成根 AGENTS.md、模块 AGENTS.md 和 docs/vibecoding 知识库，不要改业务代码。
```

预期关注点：

- Lead skill 选择 `vibecoding-knowledge-base`。
- Supporting skill 只在模块边界、API 契约或 Netty 协议解释需要时选择对应 Java 专项 skill。
- 明确禁止修改业务代码、SQL、配置和测试。
- 输出知识库范围、证据来源、待确认项和验证方式。

### Input Sample

```text
现有 common、cms-api、sdk-api 三个模块，需要生成 AI 编程知识库和模块导航。
```

### Expected Findings

- rule: 知识库、AGENTS.md 和 docs/vibecoding 任务应选择 `vibecoding-knowledge-base`。
  keyword: `vibecoding-knowledge-base`
- rule: 模块边界不清时才使用 `java-multi-module-architecture` 支撑。
  keyword: `java-multi-module-architecture`
- rule: 不得修改业务代码、SQL、配置或测试。
  keyword: 不要改业务代码
