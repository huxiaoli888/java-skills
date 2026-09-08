# 输出模板

## 目录

- [模板维护边界](#模板维护边界)
- [模板索引](#模板索引)

## 模板维护边界

本文件只承载交付模板索引，不作为协议、安全、响应、集群或观测规则的 source reference。模板中的字段和检查项只提醒交付物覆盖范围；具体口径以对应 reference 为准：协议 envelope、`func/version/reqid/ts/seqno` 和字段边界以 `protocol-format.md` 为准；响应 JSON、ACK 和错误码以 `response-contract.md` 为准；签名原文、canonical builder、body hash、query 排序和防重放以 `signature-canonicalization.md` 为准；WebSocket 握手、首条 `AUTH`、连接治理和消息级签名以 `netty-websocket.md` 为准；TCP/UDP 拆包粘包、UDP route、ACK/重试和 I/O 线程边界以 `netty-tcp-udp.md` 为准；集群连接映射、UDP route 映射、跨节点通知和节点下线治理以 `cluster-routing.md` 为准；日志、metrics、告警、测试和压测验收以 `observability-testing.md` 为准。

修改模板中的协议、安全、响应、集群或观测检查项前，必须先更新对应 source reference，再同步对应 `references/templates/*.md` 子模板和自检脚本。

## 模板索引

| 交付物 | 模板文件 | 适用场景 |
| --- | --- | --- |
| 快速评审 | `references/templates/design-review-template.md` | 判断现有 UDP/TCP/WebSocket 设计是否合理 |
| 架构决策记录 | `references/templates/adr-template.md` | 记录为什么选择 Netty UDP/TCP/WebSocket、`func + version`、集群路由方案 |
| 协议说明书 | `references/templates/protocol-spec-template.md` | 给客户端、服务端和测试人员对齐协议 |
| 集群路由方案 | `references/templates/cluster-routing-template.md` | 设计跨节点通知、在线映射、ACK、重试 |
| 压测报告 | `references/templates/load-test-report-template.md` | 验证连接数、吞吐、延迟、资源和瓶颈 |
