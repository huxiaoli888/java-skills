# Netty WebSocket 设计与参数模板




## 目录

- [选型规则](#选型规则)
- [推荐 Pipeline](#推荐-pipeline)
- [线程模型](#线程模型)
- [ServerBootstrap ChannelOption](#serverbootstrap-channeloption)
- [Pipeline 参数](#pipeline-参数)
- [鉴权生命周期](#鉴权生命周期)
- [背压和慢消费者](#背压和慢消费者)
- [ByteBuf 和泄漏检测](#bytebuf-和泄漏检测)
- [基础配置模板](#基础配置模板)
- [WebSocket 落地边界](#websocket-落地边界)
- [参数验收清单](#参数验收清单)

## 选型规则

选择 Netty WebSocket 的原因：

- 更适合高并发长连接、低延迟消息收发和自定义协议栈。
- 线程模型、Channel 生命周期、背压、ByteBuf、心跳和连接关闭控制更直接。
- 适合与 UDP/TCP/私有协议统一在 Netty 技术栈下治理。
- 更容易按 `func + version` 构建协议解析、分发、限流和统计管线。

选型矩阵：

| 场景 | 推荐 | 说明 |
| --- | --- | --- |
| 高并发设备长连接 | Netty WebSocket | 默认选择 |
| UDP/TCP/WebSocket 共存 | Netty WebSocket | 统一线程模型和协议治理 |
| 自定义二进制协议 | Netty WebSocket | 更好控制 ByteBuf 和编解码 |
| 只做后台管理页通知 | Spring WebSocket | 连接数少、开发快 |
| 已有 Spring WebSocket 基础设施 | Spring WebSocket 可接受 | 需补齐限流、心跳、观测和分发规则 |
| 对消息顺序、背压、慢消费者敏感 | Netty WebSocket | 更容易做精细控制 |

## 推荐 Pipeline

```text
ServerBootstrap
  -> HttpServerCodec
  -> HttpObjectAggregator
  -> HttpUpgradeAuthHandler
  -> WebSocketServerProtocolHandler
  -> IdleStateHandler
  -> WsFrameDecoder
  -> WsAuthMessageHandler
  -> WsMessageDispatcher
  -> writer/NettyResponseWriter
```

Pipeline 说明：

- `HttpUpgradeAuthHandler` 在 WebSocket Upgrade 前校验 path、Origin、限流、`authorization`、`x-reqid`、`x-timestamp`、`x-sign`、`x-sign-alg`、`x-api-version`、`x-api-key`，失败时返回 HTTP 错误，不进入 WebSocket 握手；历史项目已有 `appKey/keyId` 时只能作为兼容别名。
- `WebSocketServerProtocolHandler` 只负责 WebSocket 协议升级和控制帧处理，不承载业务鉴权。
- `WsAuthMessageHandler` 只处理握手后仍需首条 `AUTH` func 的场景；认证完成前不得放行业务 `func`。
- `WsMessageDispatcher` 在分发已认证业务消息前，必须按 `func` 风险等级调用 `protocol/MessageSecurityEnvelopeFields.java` 解析 `sign/sign-alg/api-key`，高风险消息未携带消息级签名材料时抛出类型化鉴权失败，由 `writer/NettyResponseWriter.java` 按 `response-contract.md` 映射最终 `code`。

本文件不定义具体 `AC000x` 错误码；WebSocket transport 只产生类型化失败原因，最终响应 `reqid/code/message/ts/data` 由 `writer/NettyResponseWriter.java` 统一写出。

## 线程模型

| 参数 | 建议 | 说明 |
| --- | --- | --- |
| `bossGroupThreads` | `1` 或 `2` | 只负责 accept |
| `workerGroupThreads` | `CPU 核数 * 2` 起步 | 负责 I/O，不执行慢业务 |
| `businessExecutor.corePoolSize` | `CPU 核数` 起步 | 处理 handler 业务逻辑 |
| `businessExecutor.maxPoolSize` | `CPU 核数 * 2~4` | 依赖 Redis/MQ/DB 时按压测调整 |
| `businessExecutor.queueCapacity` | 有界队列，如 `1000~10000` | 禁止无界队列 |
| `logExecutor` | 独立线程池 | 慢日志和审计日志隔离 |

规则：

- EventLoop 只做解码、轻校验、路由和写回。
- 业务线程池必须有拒绝策略，拒绝时产生服务繁忙失败并交给统一 writer 映射，或关闭低优先级连接。
- 不同优先级 `func` 可以使用不同业务线程池。
- 业务线程池队列长度必须暴露 metrics。

## ServerBootstrap ChannelOption

| 参数 | 建议值 | 说明 |
| --- | --- | --- |
| `SO_BACKLOG` | `1024` 起步 | 建连峰值高时调大 |
| `SO_REUSEADDR` | `true` | 端口复用 |
| `TCP_NODELAY` | `true` | 降低小包延迟 |
| `SO_KEEPALIVE` | `true` | TCP keepalive，不能替代应用心跳 |
| `ALLOCATOR` | `PooledByteBufAllocator.DEFAULT` | 降低分配开销 |
| `WRITE_BUFFER_WATER_MARK` | 低 `32KB` / 高 `64KB` 起步 | 慢消费者背压 |
| `AUTO_READ` | 默认 `true`，过载时可动态关闭 | 高级背压控制 |

示例：

```java
ServerBootstrap bootstrap = new ServerBootstrap()
        .group(bossGroup, workerGroup)
        .channel(NioServerSocketChannel.class)
        .option(ChannelOption.SO_BACKLOG, 1024)
        .childOption(ChannelOption.TCP_NODELAY, true)
        .childOption(ChannelOption.SO_KEEPALIVE, true)
        .childOption(ChannelOption.ALLOCATOR, PooledByteBufAllocator.DEFAULT)
        .childOption(ChannelOption.WRITE_BUFFER_WATER_MARK,
                new WriteBufferWaterMark(32 * 1024, 64 * 1024));
```

Linux 生产环境可评估 Epoll：

```text
NioServerSocketChannel -> EpollServerSocketChannel
NioEventLoopGroup      -> EpollEventLoopGroup
```

使用 Epoll 时必须确认运行环境、依赖 classifier 和容器内核支持。

## Pipeline 参数

| 参数 | 建议值 | 说明 |
| --- | --- | --- |
| `maxHttpContentLength` | `64KB` 起步 | 握手 HTTP 聚合上限 |
| `maxFramePayloadLength` | `64KB` 或按业务定义 | 单帧最大消息 |
| `allowExtensions` | 默认 `false` | 压缩会增加 CPU 和安全风险 |
| `readerIdleSeconds` | `60~120` | 多久没收到客户端消息判定空闲 |
| `writerIdleSeconds` | `0` 或按需 | 服务端写空闲检测 |
| `allIdleSeconds` | `0` 或按需 | 双向空闲检测 |
| `handshakeTimeoutMillis` | `5s~10s` | 握手超时 |
| `authTimeoutMillis` | `5s~10s` | 建连后认证超时 |

心跳建议：

- 应用层使用 `HEARTBEAT` func，便于统计和鉴权态检查。
- WebSocket ping/pong 可作为底层保活，但不要替代业务心跳。
- 心跳响应必须轻量，不进入慢业务线程池。

## 鉴权生命周期

必须先明确鉴权模式，不要把浏览器 WebSocket、SDK 长连接和 CMS 管理端混成一套隐式规则。

| 模式 | 适用场景 | 处理方式 |
| --- | --- | --- |
| `signed-upgrade` | SDK、可控 CMS 长连接客户端、能设置完整 Header 的客户端 | 在 HTTP Upgrade 阶段校验 `authorization/x-reqid/x-timestamp/x-sign/x-sign-alg/x-api-version/x-api-key`，失败不升级；这是 WebSocket Upgrade 特例，不代表 CMS HTTP/REST 后台接口需要 `x-api-key`。 |
| `auth-message` | 纯浏览器 Web 页面、自定义 Header 受限场景 | Upgrade 只校验 path、Origin、限流和短期票据；握手后第一条 `AUTH` func 携带签名材料并完成认证。 |
| `hybrid` | 同一入口兼容 CMS、SDK、Web | 优先 `signed-upgrade`；缺少签名 Header 时进入短认证窗口并要求首条 `AUTH`。 |

按 `auth.mode` 选择鉴权流程：

```text
signed-upgrade:
  HTTP Upgrade
  -> 校验 path、origin、基础限流
  -> 校验 authorization / x-reqid / x-timestamp / x-sign / x-sign-alg / x-api-version / x-api-key
  -> 握手成功后绑定基础身份
  -> AUTHENTICATED 后才允许进入业务 handler

auth-message:
  HTTP Upgrade
  -> 校验 path、origin、基础限流和短期票据
  -> 握手成功后进入 AUTHENTICATING
  -> 限定 auth-timeout-ms 内发送首条 AUTH func
  -> 校验 AUTH envelope 中的 reqid / ts / version / func / authorization / sign / sign-alg / api-key
  -> 使用 WebSocketAuthCanonicalBuilder 构造 canonical string 并按 ws-auth replay key 去重
  -> AUTHENTICATED 后才允许进入业务 handler

hybrid:
  -> 优先按 signed-upgrade 校验
  -> 缺少完整签名 Header 时进入 auth-message 的短认证窗口
```

规则：

- 浏览器 WebSocket 无法自由设置部分自定义 header 时，可以把签名材料放在短期 token、query 中的一次性握手票据或首条 `AUTH` 消息中，但服务端必须限制认证窗口，并禁止长期密钥进入 URL。
- `signed-upgrade` 模式下，`HttpUpgradeAuthHandler` 必须在 `WebSocketServerProtocolHandler` 之前完成签名验签和重放校验。
- `auth-message` 模式下，`HttpUpgradeAuthHandler` 只做 path、Origin、基础限流和短期票据校验，`WsAuthMessageHandler` 必须在 `auth-timeout-ms` 内收到首条 `AUTH`，并按 `WebSocketAuthCanonicalBuilder` 使用 envelope 顶层 `reqid/ts/api-key/sign-alg/version/func` 和原始消息体 bytes 构造签名原文。
- 认证前只允许握手、`AUTH`、底层 ping/pong；普通业务 `func` 产生认证失败响应并关闭连接，具体错误码由统一 writer 映射。
- CMS/SDK 长连接的 `signed-upgrade` 模式都应支持 `x-reqid`、`x-timestamp`、`x-sign`、`x-sign-alg`、`x-api-version`、`x-api-key`；该规则只适用于 WebSocket Upgrade，不改变 CMS HTTP/REST 不使用 `x-api-key` 的后台公参规则。历史 `appKey/keyId` 只作为兼容别名，不作为新协议推荐字段。
- `HEARTBEAT` 和 `ACK` 可依赖已认证连接，不强制每条消息签名；高风险业务 `func` 必须按消息级签名规则校验。
- `signed-upgrade` 重放缓存使用 `ws-upgrade:{x-api-key}:{x-reqid}:{authSubject|clientId}`；`auth-message` 首条 `AUTH` 使用 `ws-auth:{api-key}:{reqid}:{ticketId|authSubject|connectionId}`；已认证高风险业务消息使用 `ws-message:{api-key}:{reqid}:{authSubject|connectionId}`。如果使用短期票据，票据必须单次使用并优先作为 replay key 维度，不能只校验时间戳或只依赖 `connectionId`。

`auth-message` 首条 `AUTH` 示例：

```json
{
  "reqid": "client-generated-id",
  "func": "AUTH",
  "version": "V1",
  "ts": 1720000000000,
  "authorization": "Bearer token",
  "sign": "signature",
  "sign-alg": "HMAC-SHA256",
  "api-key": "key-id",
  "payload": {
    "ticket": "short-lived-handshake-ticket"
  }
}
```

首条 `AUTH` 使用 WebSocket 消息 envelope 顶层字段，不在 `payload` 中重复放 `x-reqid/x-timestamp/x-api-version`。`AUTH` 消息级签名按 `signature-canonicalization.md` 的业务消息 canonical string 执行，`BODY_SHA256_HEX` 使用首条 `AUTH` 原始消息体 bytes 或项目明确的 canonical payload bytes。如果浏览器无法安全保存长期密钥，`payload.ticket` 应使用后端签发的短期一次性票据。

已认证 WebSocket 高风险业务消息示例：

```json
{
  "reqid": "client-generated-id",
  "func": "TOKEN_UPLOAD",
  "version": "V2",
  "ts": 1720000000000,
  "sign": "signature",
  "sign-alg": "HMAC-SHA256",
  "api-key": "key-id",
  "payload": {}
}
```

已认证 WebSocket 消息级签名规则：

- 低风险业务消息可以不携带 `sign/sign-alg/api-key`，但仍必须有 `reqid/func/version/ts/payload`。
- 高风险业务消息必须在 envelope 顶层携带 `sign/sign-alg/api-key`；不要把 HTTP `x-reqid/x-timestamp/x-sign/x-sign-alg/x-api-version/x-api-key` 放入 `payload`。
- 高风险业务消息的 `reqid` 在 replay window 内唯一，服务端按 `ws-message:{api-key}:{reqid}:{authSubject|connectionId}` 短 TTL 去重；优先使用已认证主体，`connectionId` 只作为兜底。
- WebSocket 业务消息通常没有 `udid` 字段，签名 canonical string 的 `UDID` 槽位使用空字符串，不要求客户端伪造设备标识。
- WebSocket 有顺序语义的业务可在 `payload.seqno` 放业务顺序号；`seqno` 不替代 `reqid`，也不进入通用 envelope 顶层。
- 消息级安全字段解析使用通用 `protocol/MessageSecurityEnvelopeFields.java`，不要塞进 `WsAuthMessageHandler` 或 `WsMessageDispatcher` 的业务分支。

## 背压和慢消费者

- `channel.isWritable()` 为 false 时停止继续写大消息。
- 写队列超过阈值时丢弃低优先级通知或关闭连接。
- 对通知类消息设置最大未 ACK 数。
- 大消息改为传引用，不直接通过 WebSocket 推送。
- 单连接 outbound queue 建议默认不超过 `1000` 条或 `4MB`，以先到者为准。
- 单连接未 ACK 关键通知默认不超过 `100` 条，超过后暂停发送新关键通知并触发告警。
- 低优先级通知队列满时可以丢弃最新或合并；高风险业务响应、交易、令牌、设备绑定类消息不得静默丢弃。
- 单连接连续 `30s` 处于不可写或高水位，建议关闭连接，关闭码 `4500`，并要求客户端重连恢复业务状态。
- 队列满时优先级建议：先丢过期低优先级通知，再丢可合并状态通知，再拒绝新请求；不要丢已经处理成功但尚未响应的高风险请求结果。

| 场景 | 策略 |
| --- | --- |
| 写缓冲短暂升高 | 暂停低优先级通知 |
| 写缓冲持续高水位 | 关闭连接，关闭码 `4500` |
| ACK 积压 | 停止重发，标记客户端不可达 |
| 单连接 QPS 过高 | 按连接限流 |

## ByteBuf 和泄漏检测

开发和压测环境建议：

```text
-Dio.netty.leakDetection.level=advanced
```

生产环境可使用：

```text
-Dio.netty.leakDetection.level=simple
```

规则：

- 手动 retain/release 必须成对。
- 不要把 ByteBuf 直接传入异步线程后忘记 retain。
- 业务层不要持有 ByteBuf，进入 handler 前转换为业务对象或不可变 byte[]。
- 压测后检查 direct memory、GC 和泄漏日志。

## 基础配置模板

```yaml
websocket:
  path: /ws/mss
  auth:
    mode: signed-upgrade
  max-http-content-length: 65536
  max-frame-payload-length: 65536
  handshake-timeout-ms: 10000
  auth-timeout-ms: 10000
  reader-idle-seconds: 90
  max-connections-per-ip: 100
  max-connections-per-device: 3
  max-qps-per-connection: 20
  write-buffer-low-water-mark: 32768
  write-buffer-high-water-mark: 65536
  business-executor:
    core-size: 8
    max-size: 32
    queue-capacity: 5000

security:
  timestamp-skew-seconds: 300
  replay-ttl-seconds: 300
```

`security.timestamp-skew-seconds` 控制 WebSocket Upgrade Header `x-timestamp` 或消息 envelope `ts` 与服务端时间的允许偏差；`security.replay-ttl-seconds` 控制 `ws-upgrade/ws-auth/ws-message` replay key 的短 TTL 去重窗口。认证超时只限制连接阶段，不能替代签名防重放窗口。

## WebSocket 落地边界

WebSocket 专项类只放在 `transport/websocket/`，例如：

- `HttpUpgradeAuthHandler.java`
- `WsConnectionHandler.java`
- `WsSessionManager.java`
- `WsAuthMessageHandler.java`
- `WsMessageDispatcher.java`

UDP/TCP/WebSocket 共用的 Java/Spring 目录结构见 `implementation-layout.md`。不要把 TCP 拆包、UDP datagram 解码或业务 service 规则塞进 WebSocket 专项 handler。

实现约束：

- `MessageHandler` 不直接操作 `WebSocketSession` 或 Netty `Channel`。
- `MessageHandler` 不拼装网络响应，由 `writer/NettyResponseWriter.java` 统一处理。
- `WsMessageDispatcher` 不写业务规则，只做解析、校验、路由和异常映射。
- `WsAuthMessageHandler` 只管理首条 `AUTH` 的协议窗口，token、短期票据或设备凭据解析应委托 `security/AuthContextResolver.java`。
- 首条 `AUTH` 和已认证高风险业务消息的消息级 `sign/sign-alg/api-key` 解析应委托 `protocol/MessageSecurityEnvelopeFields.java`，不要由 WebSocket 专项 handler 自己拼字段。
- 业务 service 不依赖 Netty 或 WebSocket 类型。

## 参数验收清单

- 已设置单帧大小、握手超时、认证超时和心跳超时。
- 已设置签名时间戳偏差窗口和 `ws-upgrade/ws-auth/ws-message` 防重放 TTL。
- 已配置有界业务线程池和拒绝策略。
- 已配置写缓冲水位线和慢消费者处理策略。
- 已确认 EventLoop 中没有慢 Redis/MQ/DB/HTTP 调用。
- 已开启压测环境 ByteBuf 泄漏检测。
- 已把连接数、线程池队列、EventLoop 阻塞、写缓冲状态接入 metrics。
