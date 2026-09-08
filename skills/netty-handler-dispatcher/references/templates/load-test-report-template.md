
## 压测报告模板

````markdown
# Netty 传输协议压测报告

## 结论

- 是否达标：
- 最大稳定连接数 / UDP route 数：
- 最大稳定 QPS：
- 核心 func P99：
- 主要瓶颈：

## 测试环境

| 项 | 值 |
| --- | --- |
| 服务版本 | |
| 机器规格 | |
| 实例数 | |
| JDK | |
| Netty 版本 | |
| Transport | UDP / TCP / WebSocket |
| Redis/MQ/DB 环境 | |
| 压测工具 | |

## 参数配置

| 参数 | 值 |
| --- | --- |
| workerGroupThreads | |
| businessExecutor | |
| maxFramePayloadLength | |
| readerIdleSeconds | |
| writeBufferWaterMark | |
| maxConnectionsPerIp | |
| udpMaxDatagramBytes | |
| udpRouteTtlSeconds | |

## 压测场景

| 场景 | 连接数 / UDP route 数 | QPS | func | payload 大小 | 持续时间 | 目标 |
| --- | --- | --- | --- | --- | --- | --- |
| 建连压测 | | | | | | |
| 心跳压测 | | | HEARTBEAT | | | |
| 核心消息压测 | | | TOKEN_UPLOAD | | | |
| 通知 ACK 压测 | | | TOKEN_STATUS_NOTIFY | | | |
| 断线重连 | | | | | | |
| 慢消费者 | | | | | | |

## 结果

| 指标 | P50 | P90 | P95 | P99 | Max |
| --- | --- | --- | --- | --- | --- |
| 消息处理耗时 | | | | | |
| Redis 耗时 | | | | | |
| MQ 耗时 | | | | | |
| 写回耗时 | | | | | |

核心消息延迟、错误率、ACK 超时和限流必须按 `nodeId` 聚合，确认是否集中在单个节点或少数节点。

## 错误统计

| code | 数量 | 占比 | 说明 |
| --- | --- | --- | --- |
| [从 response-contract.md 引用] | | | [错误说明] |

## 安全事件统计

| 指标 | 数量 | 主要标签 | 说明 |
| --- | --- | --- | --- |
| `netty_signature_verify_total` | | `transport/nodeId/stage/result/signAlg/canonicalBuilder` | 验签总量，覆盖成功、失败和跳过路径，`result` 使用有限枚举 |
| `netty_signature_verify_duration_ms` | | `transport/nodeId/stage/result/signAlg/canonicalBuilder` | 验签耗时，用于评估正常请求 HMAC 成本和算法退化 |
| `netty_signature_fail_total` | | `transport/nodeId/stage/reason/signAlg/canonicalBuilder/bodyHashSource/contentTypeClass` | 签名失败，不记录签名值、密钥材料、body 原文、body hash 原值或完整 `Content-Type` |
| `netty_replay_rejected_total` | | `transport/nodeId/stage/replayKeyType/reason` | replay key 命中或短期票据重复使用 |
| `netty_timestamp_skew_rejected_total` | | `transport/nodeId/stage/reason` | `ts/x-timestamp` 超出允许时间窗口 |

## 资源使用

| 指标 | 平均 | 峰值 | 说明 |
| --- | --- | --- | --- |
| CPU | | | |
| 内存 | | | |
| Direct Memory | | | |
| GC 次数/耗时 | | | |
| EventLoop 阻塞 | | | |
| 业务线程池队列 | | | |
| 写缓冲高水位次数 | | | |
| UDP datagram 丢弃数 | | | |
| UDP route 过期数 | | | |

## 稳定性

- soak test 时长：
- 连接掉线率：
- 重连成功率：
- ACK 超时率：
- 验签成功率：
- 验签 P95/P99 耗时：
- 签名失败率：
- 重放拦截率：
- 时间戳偏差拒绝率：
- UDP datagram 丢弃率：
- UDP route 过期率：
- Redis/MQ/DB 超时率：

## 瓶颈分析

- 主要瓶颈：
- 证据：
- 优化建议：

## 风险

| 风险 | 影响 | 建议 |
| --- | --- | --- |
| | | |
````
