# API 生命周期与错误码治理标准

## 1. 目标

API 一旦被前端、移动端、H5、合作方或其他系统消费，就变成公开契约。新增项目必须定义版本、废弃、兼容性测试和错误码冻结规则，避免接口随代码重构漂移。

## 2. 版本策略

默认 URL 版本：

```text
/api/v1/{module}/{resource}
```

规则：

- `v1` 表示外部契约版本，不等于代码版本。
- 兼容新增字段不升级主版本。
- 删除字段、修改字段语义、修改错误码、修改幂等规则、修改签名输入，必须升级契约版本或提供兼容期。
- `x-api-version` 只在 URL 版本不足以表达合作方契约差异时使用。

## 3. 废弃策略

废弃接口必须记录：

```text
deprecatedAt
sunsetAt
replacementApi
affectedClients
compatibilityPlan
rollbackPlan
```

规则：

- OpenAPI 注解应标记 deprecated。
- 响应头可增加 `Deprecation` 和 `Sunset`，但不能替代正式通知。
- 高风险支付、订单、回调 API 废弃前必须完成调用方确认和灰度计划。

## 4. 错误码冻结

规则：

- 已被客户端消费的错误码不得复用为新含义。
- 错误码删除只能标记废弃，不从注册表中物理移除。
- `message` 文案可以调整，`code`、`messageKey` 和语义不得漂移。
- 新增业务错误码必须记录所属系统、模块、语义和默认消息；不得把 HTTP 状态写入错误码契约。

推荐登记字段：

```text
code, name, messageKey, defaultMessage, ownerModule, sinceVersion, deprecated
```

## 5. 契约测试

至少覆盖：

- 统一响应字段 `reqid/code/message/ts/data`。
- 参数校验错误结构。
- 认证失败、无权限、签名失败、防重放、幂等冲突错误码。
- 分页字段和页码语义。
- OpenAPI 示例和真实 DTO 一致。

外部合作方 API 应保存请求/响应样例作为回归用例。
