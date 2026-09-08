# 静态检查器覆盖矩阵

`scripts/check_java_api_standard.py` 是启发式静态检查器，用于发现明显 API 标准漂移。它不能替代编译、单元测试、集成测试、ArchUnit、人工设计评审或安全审计。

## 覆盖原则

- 每条可静态判断的标准应有稳定规则 ID。
- 每个新增规则应至少有一个负向测试 fixture。
- 请求头、profile、废弃头等容易漂移的公共契约应优先写入 `api-standard-contract.json`，checker 和 generator 后续都按它同步。
- 检查器通过只代表“未发现已覆盖规则的明显违规”，不代表项目完全生产可用。
- 无法可靠静态判断的规则应保留在人工检查清单中，不要用脆弱字符串匹配强行判断。

## 规则覆盖

| 标准领域 | 代表规则 ID | 当前覆盖方式 | 覆盖状态 |
| --- | --- | --- | --- |
| 必需基础组件 | `required-component` | 按类名检查统一响应、错误码、异常、日志、CORS、SQL 注入、限流、文件上传、审计、持久化基础组件 | 自动 |
| 环境配置 | `environment-config`、`production-config-placeholder`、`production-secret-source`、`actuator-exposure` | 检查可部署模块配置文件、生产占位值、生产密钥来源和 Actuator 暴露范围 | 自动 |
| 统一响应 | `api-result-contract`、`api-result-reqid-null-normalization`、`controller-unified-response`、`controller-raw-return` | 检查 `ApiResult` 字段、成功码、`reqid` null 归一化和 Controller 返回类型 | 自动 |
| 错误码 | `error-code-contract`、`common-error-code-contract` | 检查错误码字符串化、禁止错误码携带 `httpStatus`、通用错误码格式 | 自动 |
| 请求头和签名 | `signature-header-contract`、`signature-x-sign-contract`、`replay-component-contract` | 检查 `x-reqid`、`x-timestamp`、`x-udid`、`x-sign`、`x-sign-alg`、`x-api-version`、废弃头和 replay store 参数 | 自动 |
| 共享请求头契约 | `shared-header-contract` | 检查 CORS `allowed-headers`、关键 API 文档和废弃请求头是否与 `api-standard-contract.json` 一致 | 自动 |
| CMS/SDK 安全边界 | `cms-security-component-missing`、`sdk-security-component-missing`、`security-filter-order` | 检查安全组件存在、排除路径配置和 filter 顺序 | 自动 |
| minimal profile 裁剪 | `minimal-sdk-module-present`、`minimal-sdk-contract-residue` | 检查 minimal 输出不残留 SDK 模块或强 SDK 契约文案 | 自动 |
| 模块依赖 | `maven-module-boundary`、`layer-dependency` | 检查 Maven 模块互相依赖和明显层间导入违规 | 自动 |
| DTO/Entity 边界 | `controller-entity-import`、`validation-message-i18n`、`lombok-sensitive-tostring` | 检查 Controller 导入 entity、校验消息和敏感对象 `@Data/@ToString` | 自动 |
| SQL 安全 | `sql-injection-risk`、`complex-sql-should-use-xml` | 检查 Mapper/Repository 中 `${}` 和复杂 SQL 注解 | 自动 |
| 异常处理 | `exception-swallowed`、`business-exception-control-flow` | 检查 `catch` 块是否空处理、只返回默认值、只写 `warn` 或缺少 `log.error`/继续抛出/onError 回调；启发式发现 service/domain/application 层把正常业务失败写成 `BusinessException` 控制流 | 自动 + 人工 |
| 高风险交易 | `idempotency-missing`、`replay-protection-missing`、`signature-missing` | 发现订单、支付、退款 Controller 后检查幂等、防重放和签名组件 | 自动 |
| 审计日志细节 | `operation-audit-contract` | 检查审计注解、切面、记录模型和服务接口基础契约 | 自动 |
| 真实权限模型 | 无 | 权限码、角色、菜单、租户和数据权限语义需要按业务评审 | 人工 |
| 业务幂等语义 | 部分由 `idempotency-component-contract` 覆盖 | 只能检查命名和组件存在，不能证明业务唯一键选择正确 | 人工 + 测试 |
| 生产替换落地 | 部分由 `production-*` 规则覆盖 | 只能发现明显开发占位，不能证明 Redis/JDBC/网关/密钥系统已正确接入 | 人工 + 集成测试 |

## 检查结果输出要求

使用本 checker 做评审或生成结果验收时，最终回复必须同时包含：

- 自动检查结果：命令、profile、错误数和警告数。
- 人工检查边界：列出本矩阵中仍需人工确认的权限模型、业务幂等语义、生产替换落地、真实 SQL 执行计划和集成测试结论。
- 未验证项：如果没有运行 Maven、集成测试、ArchUnit、真实 Redis/JDBC/网关替换验证，必须明确说明。

不要把 “checker 通过” 表述为 “项目已经生产可用”。

## 新增规则流程

1. 在对应 reference 中补充标准描述。
2. 在本矩阵登记规则 ID、覆盖方式和覆盖状态。
3. 在 checker 中新增最小启发式规则。
4. 在 `scripts/test_check_java_api_standard.py` 增加负向 fixture。
5. 使用生成器 base-template 跑 standard profile 回归，确认规则不会误伤标准模板。
