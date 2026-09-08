# Fixture: 场景三：响应与 ACK 字段边界

响应和 ACK 顶层统一使用 reqid/code/message/ts/data
ACK 不是入站业务 handler，不注册 ACK + V1
