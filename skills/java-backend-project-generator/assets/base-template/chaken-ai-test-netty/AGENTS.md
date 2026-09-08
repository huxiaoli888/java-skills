# Netty 模块规则

- 本模块只负责 TCP/UDP/WebSocket 传输入口、协议 envelope、鉴权、心跳、ACK、统一响应和 handler dispatcher。
- 业务逻辑必须进入 service/application service，不要写在 Netty channel handler 中。
- 不要让业务 service 依赖 Netty `Channel`、`ChannelHandlerContext` 或 `DatagramPacket`。
- 响应和 ACK 统一使用 `reqid/code/message/ts/data`，错误码与 HTTP API 保持一致。
- 高风险消息必须携带 `sign/sign-alg/api-key`，TCP/UDP 同时携带 `udid`。
