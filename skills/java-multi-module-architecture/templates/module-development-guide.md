# 模块开发指南

## 新增功能定位

| 场景 | 修改位置 | 注意事项 |
| --- | --- | --- |
| HTTP API 入参/出参 | API 或 connector 模块 | 保持兼容，避免污染 MQ 或协议模型 |
| 核心业务规则 | core 或 service 模块 | 不依赖 controller，不直接处理展示格式 |
| 外部系统调用 | integration/outside/client 模块 | 处理超时、降级、脱敏日志 |
| MQ 消费 | consumer 模块 | 明确 topic、group、tag、幂等和重试 |
| 共享稳定契约 | common/contract/client 模块 | 只放稳定内容，不放业务实现 |

## 新增模块检查

- 模块职责是否能用一句话说明。
- 是否真的需要独立部署。
- 上游和下游是否明确。
- 是否引入循环依赖。
- 是否有最小验证命令。
