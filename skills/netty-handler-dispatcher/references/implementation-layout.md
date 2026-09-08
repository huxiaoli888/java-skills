# Java/Spring 落地结构




## 目录

- [适用场景](#适用场景)
- [推荐目录](#推荐目录)
- [职责边界](#职责边界)
- [Registry 示例](#registry-示例)

## 适用场景

当用户要求实现或重构 Netty UDP/TCP/WebSocket dispatcher 时读取本文件。这里给出通用 Java/Spring 模块落地结构，WebSocket 专项参数继续看 `netty-websocket.md`，TCP/UDP 专项编解码继续看 `netty-tcp-udp.md`。

## 推荐目录

```text
transport/
  websocket/
    HttpUpgradeAuthHandler.java
    WsConnectionHandler.java
    WsSessionManager.java
    WsAuthMessageHandler.java
    WsMessageDispatcher.java
  tcp/
    TcpServerHandler.java
    TcpFrameDecoder.java
    TcpAuthHandler.java
    TcpMessageDispatcher.java
  udp/
    UdpServerHandler.java
    UdpDatagramDecoder.java
    UdpMessageDispatcher.java
protocol/
  MessageEnvelope.java
  MessageKey.java
  MessageParser.java
  HttpHeaderSecurityFields.java
  MessageSecurityEnvelopeFields.java
  TcpUdpSecurityEnvelopeFields.java
router/
  MessageHandlerRegistry.java
handler/
  MessageHandler.java
  V2TokenUploadHandler.java
  DeviceStatusReportHandler.java
security/
  canonical/
    CanonicalRequest.java
    HttpRequestCanonicalBuilder.java
    WebSocketUpgradeCanonicalBuilder.java
    WebSocketAuthCanonicalBuilder.java
    WebSocketMessageCanonicalBuilder.java
    TcpAuthCanonicalBuilder.java
    TcpUdpMessageCanonicalBuilder.java
  AuthContextResolver.java
  SignatureVerifier.java
  ReplayKeyResolver.java
  ReplayCache.java
observability/
  SecurityEventLogger.java
  NettyMetricsBinder.java
writer/
  NettyResponseWriter.java
service/
  TokenApplicationService.java
  DeviceStatusApplicationService.java
```

## 职责边界

- `transport/*` 只处理连接、帧、datagram、基础限流和协议入口。
- `protocol/*` 只处理 envelope、字段解析、字段校验和解析结果；不做响应 JSON 或错误码映射，解析失败只返回类型化失败原因。
- `protocol/MessageSecurityEnvelopeFields.java` 只解析 WebSocket 首条 `AUTH`、TCP `AUTH`、TCP/UDP 高风险消息和已认证 WebSocket 高风险业务消息 envelope 顶层 `sign/sign-alg/api-key`，不解析 HTTP Header、`udid`、`authorization` 或主体身份。
- `protocol/TcpUdpSecurityEnvelopeFields.java` 只解析 TCP/UDP envelope 顶层 `udid/authorization` 和匿名公开探测边界，不承载已认证 WebSocket 业务消息字段。
- `router/*` 只做 `func + version` 到 handler 的显式注册和查找，不承载具体业务 handler。
- `handler/*` 只定义 `MessageHandler` 接口和具体入站业务 handler，只做消息级 DTO 适配并调用 service。
- `security/canonical/*` 只做不同入口的 canonical request 构造，不读取密钥、不比较签名；`CanonicalRequest.java` 必须显式承载 `UDID/KEY_ID/SIGN_ALG` 槽位。
- `security/AuthContextResolver.java` 只做 token、短期票据或设备凭据到认证主体的解析与上下文构造，不承载 WebSocket transport 生命周期或具体业务规则。
- `security/ReplayKeyResolver.java` 只从已解析安全字段构造 replay key；具体 replay key 形状以 `signature-canonicalization.md` 的防重放规则为准；不做 TTL 缓存存取、业务幂等结果保存或重新定义 replay key 形状。
- `security/ReplayCache.java` 只使用 `ReplayKeyResolver` 输出的 replay key 做短 TTL 去重，可保存脱敏传输响应摘要；不重拼 canonical string，不构造 replay key，不保存业务幂等结果，不做模糊连接身份去重。
- `security/*` 只做签名验签、防重放、鉴权上下文构造。
- `observability/SecurityEventLogger.java` 只记录鉴权、签名、重放和时间戳安全事件；字段使用有限枚举 `securityStage/signAlg/canonicalBuilder/contentTypeClass/bodyHashSource/replayKeyType`，不记录完整签名、完整 replay key、token、`api-key` 原值、完整 `Content-Type`、body 原文或 body hash 原值。
- `observability/NettyMetricsBinder.java` 只发布 `netty_*` 指标；签名失败指标使用 `transport/nodeId/stage/reason/signAlg/canonicalBuilder/bodyHashSource/contentTypeClass` 这类有限枚举或低基数标签，不使用 `reqid/connectionId/userId/udid/IP/bodyHash` 等高基数字段。
- `service/*` 承载业务规则，不依赖 Netty `Channel`、`ChannelHandlerContext` 或 WebSocket 类型。
- `writer/NettyResponseWriter.java` 按 `response-contract.md` 统一响应 JSON、ACK、错误码映射和日志脱敏；响应和 ACK 只写 `reqid/code/message/ts/data`，禁止顶层 `func/version/traceId/status`，不按 UDP/TCP/WebSocket 拆协议专属 writer。

## Registry 示例

```java
@Component
public class MessageHandlerRegistry {
    private final Map<MessageKey, MessageHandler<?, ?>> handlers;

    public MessageHandlerRegistry(List<MessageHandler<?, ?>> handlerList) {
        this.handlers = handlerList.stream()
                .collect(Collectors.toMap(MessageHandler::key, Function.identity()));
    }

    public MessageHandler<?, ?> get(MessageKey key) {
        MessageHandler<?, ?> handler = handlers.get(key);
        if (handler == null) {
            throw new UnsupportedMessageHandlerException(key);
        }
        return handler;
    }
}
```
