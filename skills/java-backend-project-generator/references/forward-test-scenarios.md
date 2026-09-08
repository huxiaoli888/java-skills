# Forward-Test 场景

这些场景用于验证 `$java-backend-project-generator` 是否能正确选择 profile、尊重版本边界，并把后续业务开发路由给对应权威 skill。

## 场景一：默认轻量后台脚手架

### Input Sample

```text
帮我从零生成一个 chaken-order Java 后端项目。
```

### 预期关注点

- 选择默认 `minimal` profile。
- 生成 `common + cms-api`，依赖方向为 `cms-api -> common`。
- 不生成 `sdk-api`，除非用户明确要求 SDK 接口、开放接口或 `standard profile`。
- 不生成 Netty 模块，除非用户明确要求 TCP、UDP、WebSocket 或长连接。
- 生成后运行 Maven 编译、API 标准检查和生成器自检。

### Expected Findings

- keyword: `minimal`
- keyword: `common + cms-api`
- keyword: `不生成 sdk-api`
- keyword: `不生成 Netty 模块`
- keyword: `API 标准检查`

## 场景二：minimal 小项目

### Input Sample

```text
生成一个最小后台项目，只需要 common 和 cms-api，先不要 SDK。
```

### 预期关注点

- 选择 `minimal` profile。
- 只生成 `common + cms-api`。
- 不生成 `sdk-api`、Netty 模块或生产增强包。
- 说明生产增强只保留在路线图，不是当前脚本参数。

### Expected Findings

- keyword: `minimal`
- keyword: `common + cms-api`
- keyword: `不生成 sdk-api`
- keyword: `不生成 Netty 模块`
- keyword: `生产增强只保留路线图`

## 场景三：显式 Netty 长连接

### Input Sample

```text
生成一个订单项目，需要后台接口、SDK 接口，还要 TCP 长连接和 UDP 协议入口。
```

### 预期关注点

- 因为用户明确要求 SDK 接口，应选择 `standard` profile。
- 在 `standard` profile 基础上启用 `-IncludeNetty`。
- 额外生成 `{projectName}-netty`，且只依赖 `common`。
- Netty 模块必须包含 TCP/UDP 基础入口、`func + version` dispatcher、AUTH、HEARTBEAT、ACK/统一响应、鉴权防篡改占位、日志和基础测试。
- Netty 协议规则引用 `netty-handler-dispatcher`，统一响应和错误码引用 `java-backend-api-standard`。

### Expected Findings

- keyword: `-IncludeNetty`
- keyword: `{projectName}-netty`
- keyword: `func + version`
- keyword: `AUTH`
- keyword: `HEARTBEAT`
- keyword: `netty-handler-dispatcher`
