---
name: netty-handler-dispatcher
description: Use when 需要设计、评审或重构 Netty UDP/TCP/WebSocket 协议入口、TCP/WebSocket 长连接治理、Socket 或私有协议入口、handler dispatcher、func + version 分发、envelope、令牌上传/下载、心跳、ACK、推送、状态同步、签名、防重放、event loop 阻塞风险、集群路由、背压、压测或协议说明书。
---

# Netty Handler Dispatcher

本技能用于设计或评审“Netty 传输入口 + 协议解析 + handler 分发 + 业务服务复用”的后端架构。

本技能是 Netty TCP/UDP/WebSocket 协议入口和 handler dispatcher 的权威来源。HTTP/API 契约和通用安全字段由 `java-backend-api-standard` 维护；具体 Spring Boot 业务实现由 `java-microservice-dev` 承接；模块归属和依赖方向由 `java-multi-module-architecture` 判断。

核心原则：**不要按每种动作创建一个连接或端口；要按消息功能 `func + version` 分发到 handler，并复用稳定业务 service。**

默认技术取向：

- Netty UDP：一个端口承载同一业务域的短请求短响应，通过报文中的显式 `func + version` 或兼容规则分发 handler。
- Netty TCP：一个业务域连接承载多类消息，通过 envelope 中的 `func + version + reqid` 分发 handler。
- WebSocket：默认使用 **Netty WebSocket**，一个业务域长连接承载多类消息，通过 envelope 中的 `func + version + reqid` 分发 handler。
- 响应 JSON：通用字段和错误码格式沿用 `java-backend-api-standard`；Netty ACK、envelope、连接态和协议错误边界见 `references/response-contract.md`。响应体使用 `reqid + code + message + ts + data`，不返回 `func/version/traceId/status`，通过 `reqid` 和客户端上下文匹配请求。
- 业务逻辑：不要写在传输 handler 中，应进入可复用的 application service / domain service。
- 状态：TCP/WebSocket 连接态可以存在 session 中，UDP 上层 route 必须短 TTL；核心业务态必须落 Redis、数据库、MQ 或其他可靠状态系统。

## 任务识别

技能加载后，先识别用户任务属于哪一类，再选择最小执行模式：

- 新入口设计：UDP、TCP、WebSocket、Socket、Netty、长连接或私有协议入口。
- 连接模型判断：一个连接承载多个消息类型，还是多个连接/多个端口分别处理不同动作。
- 消息分发规则：令牌上传、令牌下载、心跳、ACK、推送、状态同步等。
- 迁移设计：从 UDP 短请求短响应、TCP 或 HTTP 扩展到 Netty WebSocket。
- 设计评审：handler 分发、event loop 阻塞、状态一致性、协议兼容和集群路由风险。
- 文档交付：协议 handler 设计文档、ADR、AGENTS.md 规则、协议说明书、集群路由方案或压测报告。

## 执行模式

根据用户目标选择最小模式：

| 模式 | 使用场景 | 必须输出 | 禁止输出 |
| --- | --- | --- | --- |
| `quick-advice` | 用户只问是否合理、怎么选 | 结论、关键理由、推荐方案 | 大段模板、代码骨架 |
| `design-review` | 评审现有 UDP/TCP/WebSocket 设计 | 优点、缺点、风险、优化建议、优先级 | 直接改业务代码 |
| `new-protocol-design` | 设计新传输协议入口 | Endpoint、envelope、func 表、handler 分发、统一响应、错误码、状态规则 | 未确认就生成完整代码 |
| `migration-design` | 从 UDP/TCP/HTTP 扩展到 WebSocket | 兼容策略、分阶段迁移、灰度、回滚、观测指标 | 一次性替换旧协议 |
| `performance-review` | 关注吞吐、延迟和阻塞风险 | 线程模型、慢依赖隔离、限流、压测指标、瓶颈风险 | 声称性能达标但无压测证据 |
| `implementation-plan` | 用户要求落地实现方案 | 文件职责、类设计、线程池、Netty 参数、测试计划 | 跳过确认直接大改 |
| `docs-only` | 只形成规则或文档 | Markdown 规范、ADR、协议文档、AGENTS.md 片段 | 修改业务代码 |

若用户只要求分析，不要修改业务代码。

## 瘦身导航

本技能的细节拆在 `references/` 中。使用时不要一次读取全部引用，按任务只读必要文件。

| 用户意图 | 优先读取 | 输出长度 |
| --- | --- | --- |
| “这种设计是否合理” | 主文件的必查反模式 + `references/protocol-format.md` 的统一架构 | 短 |
| “UDP、TCP 和 WebSocket 怎么设计” | `references/protocol-format.md` + `references/netty-tcp-udp.md` | 中 |
| “生成协议文档” | `references/protocol-format.md` + `references/templates.md`，再按索引读取对应 `references/templates/*.md` 子模板；涉及 TCP/UDP 读 `references/netty-tcp-udp.md`，涉及签名读 `references/signature-canonicalization.md`，涉及响应读 `references/response-contract.md` | 中 |
| “做 Netty WebSocket 方案” | `references/netty-websocket.md` + `references/protocol-format.md` | 中/长 |
| “设计 HTTP/REST、连接或消息签名/防篡改” | `references/protocol-format.md` + `references/signature-canonicalization.md` | 中 |
| “统一响应/错误码/响应字段” | `references/response-contract.md` | 中 |
| “从 UDP/TCP 迁移到 WebSocket” | `references/protocol-format.md` + `references/netty-tcp-udp.md` + `references/cluster-routing.md` | 中/长 |
| “设计集群路由” | `references/cluster-routing.md` | 中/长 |
| “评估性能或压测” | `references/observability-testing.md`；涉及 WebSocket 读 `references/netty-websocket.md`，涉及 TCP/UDP 读 `references/netty-tcp-udp.md` | 中 |
| “生成 ADR/协议说明书/压测报告” | `references/templates.md` | 中/长 |
| “做代码实现计划” | `references/implementation-plan.md` + `references/implementation-layout.md` + `references/protocol-format.md` + `references/observability-testing.md`；涉及签名读 `references/signature-canonicalization.md`，涉及集群读 `references/cluster-routing.md`，涉及响应读 `references/response-contract.md` | 长 |

输出控制：

- 简单问答只给结论和 3-5 条理由。
- 方案设计输出结构化表格和关键流程，不粘贴所有模板。
- 代码实现前必须先说明会新增/修改哪些文件以及职责。
- 未经用户要求，不主动生成 ADR、压测报告或完整协议文档。
- 用户明确“只分析”时，不写文件、不改代码。

## 引用文件

按需读取以下文件：

- `references/protocol-format.md`：UDP/TCP/WebSocket 统一分发、envelope、`func` 命名、生命周期、幂等、顺序、重试、超时、安全、协议格式选择。
- `references/response-contract.md`：Netty handler 统一响应 JSON、错误码 `SMEEEE`、`reqid/code/message/ts/data` 字段边界。
- `references/implementation-plan.md`：代码实现计划模板，明确新增/修改文件、职责边界和验证方式。
- `references/implementation-layout.md`：Java/Spring 通用落地结构，说明 UDP/TCP/WebSocket 目录与职责边界。
- `references/signature-canonicalization.md`：HTTP/REST、WebSocket、TCP、UDP 签名原文、字段顺序、GET/POST JSON/CMS 表单 body hash、query 排序、算法选择和防重放边界。
- `references/netty-websocket.md`：Netty WebSocket 选型、Pipeline、线程模型、ChannelOption、IdleStateHandler、背压、ByteBuf、YAML 配置、WebSocket 落地边界。
- `references/netty-tcp-udp.md`：Netty TCP/UDP 的拆包粘包、二进制 envelope、UDP ACK/重试、幂等和 I/O 线程边界。
- `references/cluster-routing.md`：多实例连接映射、跨节点通知路由、Redis Pub/Sub、Redis Stream、RocketMQ、Kafka、服务内 RPC 取舍。
- `references/observability-testing.md`：日志字段、metrics、告警、最小测试集、压测指标。
- `references/templates.md`：交付模板索引，按任务指向 `references/templates/*.md` 子模板。
- `references/templates/*.md`：设计评审、ADR、Netty 传输协议说明书、集群路由设计、压测报告等具体模板。
- `references/forward-test-scenarios.md`：维护本技能后用于前向验证的样例任务和预期关注点，普通 Netty 任务不必默认读取。
- `references/contract-rules.json`：自检脚本读取的关键契约词表、replay key 词表、CMS/SDK/WebSocket 签名边界和实现计划高频变更断言；修改安全字段、replay key 或调用方身份规则时先同步这里，再同步 source reference。

## 规则归属与更新顺序

多个 reference 会摘要同一类规则。修改共享规则时，先修改 source reference，再同步依赖摘要、模板和自检脚本，避免多处文档漂移。

唯一归属：

- `protocol-format.md` 是协议 envelope、`func/version/reqid/ts/seqno`、传输边界、幂等/顺序/重试/超时总览的唯一归属。
- `response-contract.md` 是 Netty 响应 JSON、ACK、envelope 响应边界和协议错误映射的唯一归属；通用响应字段和错误码格式与 `java-backend-api-standard` 保持一致，其他 Netty 文件只能引用摘要。
- `signature-canonicalization.md` 是签名原文、防重放、body hash、query 排序和 canonical builder 边界唯一归属；其他文件不要重新定义字段顺序。
- `netty-websocket.md` 是 WebSocket Pipeline、握手认证、首条 `AUTH`、连接治理和 WebSocket 消息级签名实现细节的唯一归属。
- `netty-tcp-udp.md` 是 TCP/UDP 拆包粘包、UDP route、ACK/重试、TCP/UDP envelope 和 I/O 线程边界的唯一归属。
- `cluster-routing.md` 是多实例连接映射、UDP route 映射、跨节点通知和节点下线治理的唯一归属。
- `observability-testing.md` 是日志、metrics、告警、最小测试集和压测验收指标的唯一归属。
- `implementation-plan.md` 和 `implementation-layout.md` 只承载落地计划和代码结构，不重新定义协议字段或签名规则。
- `templates.md` 只承载交付模板；模板中的协议、安全、响应、集群和观测条目必须来自对应 source reference。

更新顺序：

1. 先修改 source reference。
2. 再同步 `templates.md`、`implementation-plan.md`、`implementation-layout.md` 中的摘要或检查项。
3. 最后更新并运行 `scripts/check_netty_handler_dispatcher_skill.py`。

## 自检脚本

- 修改本技能后运行 `scripts/check_netty_handler_dispatcher_skill.py`。
- 维护 forward-test 场景后运行 `scripts/run_forward_tests.py`；追加 `--prompts` 可输出可复制给人工或子任务执行的测试 prompt；它只检查场景结构和列出样例，不能替代人工或子任务真实验证。
- 在 Windows 上运行系统 `quick_validate.py` 时，先设置 `$env:PYTHONUTF8='1'`，避免默认 GBK 解码 UTF-8 中文技能文件失败。
- 自检覆盖重点：
  - 技能结构：frontmatter 是否只包含 `name/description`、根目录是否只保留 `SKILL.md/agents/references/scripts`、`agents/` 和 `scripts/` 是否只包含登记文件、是否残留 README/CHANGELOG 等辅助文档、引用文件是否存在、错误拼写旧目录是否残留、长 reference 是否有目录、`agents/openai.yaml` UI 元数据是否完整且与技能触发能力一致。
  - 响应契约：错误码是否回退到旧数字码、响应契约是否保留 `SMEEEE`。
  - 安全字段：WebSocket Header 是否保留 `x-reqid/x-timestamp/x-sign/x-sign-alg/x-api-version/x-api-key`；WebSocket 高风险业务消息是否使用 envelope 顶层 `sign/sign-alg/api-key` 和 `ws-message:{api-key}:{reqid}:{authSubject|connectionId}` 防重放；TCP/UDP envelope 是否使用 `reqid/ts/version` 且高风险或已识别设备请求使用 `udid/sign/sign-alg/api-key`；匿名公开探测可省略 `udid` 和签名材料。
  - 协议边界：顺序字段是否使用 `seqno`、签名原文是否包含 `UDID`、`KEY_ID` 和 `SIGN_ALG`、HTTP/REST GET/POST JSON/CMS 表单 query/body hash 来源是否明确、canonical builder 是否按入口拆分且 `SignatureVerifier` 不构造 canonical string。
  - 配置参数：WebSocket 是否包含 `websocket.auth-timeout-ms`、`websocket.max-frame-payload-length` 和全局 `security.timestamp-skew-seconds/security.replay-ttl-seconds`；TCP/UDP 是否包含 `tcp.max-frame-bytes`、`udp.max-datagram-bytes`、`udp.route-ttl-seconds`、`rate-limit.max-qps-per-udid` 等基础参数。
  - 长连接实现：WebSocket 是否明确 `signed-upgrade/auth-message` 与首条 `AUTH` 示例、实现计划与通用落地结构是否覆盖 UDP/TCP/WebSocket 和 `handler/` 目录。
  - 模板和观测：所有 Markdown fence 是否闭合、服务端通知是否使用 publisher/writer 语义、集群路由是否使用 `netty:conn` 且包含 `connectionEpoch`、兼容测试是否覆盖 UDP/TCP/HTTP 与 Netty UDP/TCP/WebSocket、观测指标是否使用 `netty_*`。
- 自检通过不代表某个业务项目已经生产可用；它只证明技能文档内部关键契约没有明显漂移。

## 统一分层

| 层 | 职责 | 禁止事项 |
| --- | --- | --- |
| Transport | UDP datagram、TCP/WebSocket 连接接收、连接生命周期或 UDP route TTL、基础限流 | 写复杂业务规则 |
| Protocol Parser | ASN.1/JSON/Protobuf/byte[] 解析、基础格式校验 | 访问数据库或外部系统 |
| Router/Registry | 根据 `func + version` 找 handler | 硬编码巨大 `if/else` |
| Handler | 消息级适配、DTO 转换、调用 service | 承载完整业务流程 |
| Service | 业务规则、状态编排、幂等、Redis/MQ/DB | 感知具体网络连接细节 |
| Response Writer | 统一响应、ACK、错误码、日志脱敏 | 泄漏敏感字段或在响应 JSON 中返回 `func/version/traceId/status` |

## Handler 注册规则

优先使用显式 `MessageKey(func, version) -> MessageHandler` registry，不要依赖字符串拼接 bean 名称。示例保留真实入站业务：`TOKEN_UPLOAD + V2 -> V2TokenUploadHandler`、`TOKEN_DOWN + V2 -> V2TokenDownHandler`、`HEARTBEAT + V1 -> HeartbeatHandler`、`DEVICE_STATUS_REPORT + V1 -> DeviceStatusReportHandler`。Java/Spring 项目应在启动时收集所有 `MessageHandler` bean，校验 key 不重复；handler 接口和包布局细节见 `references/implementation-layout.md`。

## 响应 JSON 规则

通用字段和错误码格式参考 `java-backend-api-standard` 的统一 API 契约；Netty ACK、envelope、连接态、协议错误映射和响应字段边界见 `references/response-contract.md`。

Netty 响应字段语义与 Java API 标准保持一致，但 ACK、envelope、连接态、重试、乱序和协议错误边界由本技能负责。

摘要规则：成功 `code=000000`；失败使用 `SMEEEE` 格式稳定错误码；响应必须包含 `reqid/code/message/ts/data`；响应体不返回 `func/version/traceId/status`。完整示例见 `references/response-contract.md`。

## 必查反模式

发现以下情况应明确指出风险：每个业务动作创建一个 WebSocket/TCP 连接或 UDP 端口；一个 handler 同时处理连接鉴权、协议解析、业务规则、Redis/MQ、外部调用和日志；只靠报文长度判断新协议类型；handler 名称由字符串拼接并在运行期查 bean；EventLoop 或 WebSocket I/O 线程中执行慢 Redis、MQ、DB、HTTP 或复杂密码计算；长连接 session 保存唯一业务事实；没有 `reqid`、没有 `func + version` registry、`func` 中混入版本号、没有 ACK/超时/重试/幂等；没有 TCP/WebSocket 连接鉴权窗口、心跳超时和关闭码，或没有 UDP route 短 TTL 和限流；错误码在 HTTP、Netty UDP、Netty TCP、Netty WebSocket 三套入口含义不一致；响应 JSON 同时返回 `status` 和 `code`，或响应 JSON 返回 `func`；业务 service 直接依赖 Netty `ChannelHandlerContext`、`Channel` 或 `WebSocketSession`；将鉴权失败、签名失败、重放请求、参数错误、资源不存在、状态不允许、限流命中、幂等冲突等正常协议拒绝或业务失败写成异常控制流，并打印 `log.error` 堆栈；Netty handler、dispatcher、pipeline 或鉴权组件捕获异常后只返回错误响应、只写注释、空处理、只用 `warn` 记录或直接忽略；日志输出完整 token、credential、手机号、身份证号或密钥材料。

## 验收标准

设计或实现完成后必须满足：入口按业务域聚合，不按每个动作拆连接或端口；消息功能和版本显式存在，即 `func + version`；每类消息有独立 handler；handler 与业务 service 边界清晰；HTTP、Netty UDP、Netty TCP、Netty WebSocket 能复用同一核心业务 service；慢依赖不直接阻塞 I/O 线程；有统一错误码、统一响应结构和日志脱敏策略；正常协议拒绝和业务失败使用稳定错误码、结构化访问/安全日志和 `netty_*` 指标表达，不作为异常控制流，不打印 `log.error` 堆栈；捕获并在当前层处理的程序异常、依赖异常、编码错误、写出失败或其他不可预期异常必须使用 `log.error` 记录脱敏日志；不得吞异常；响应 JSON 遵循 `reqid/code/message/ts/data`，且不包含 `func/version/traceId/status`；有 TCP/WebSocket 心跳、鉴权、限流、超时和连接关闭策略；UDP 有 route 短 TTL、限流和过期清理策略；有幂等、ACK、重试、乱序处理规则；多实例场景有连接映射或 UDP route 映射、跨节点通知、节点下线和滚动发布策略；有可观测性指标和压测验收说明；有兼容旧协议和灰度回滚说明。

## 与其他技能协同

- Java/Spring Boot 实现时，先使用本技能确定协议和 handler 边界，再使用 Java 开发类 skill 编码。
- 做代码审查时，先使用本技能检查传输层和 handler 架构，再检查具体 Java 实现风险。
- 做项目知识库时，可把本技能输出沉淀到 `docs/vibecoding/api`、`docs/vibecoding/architecture` 或模块 `AGENTS.md`。
