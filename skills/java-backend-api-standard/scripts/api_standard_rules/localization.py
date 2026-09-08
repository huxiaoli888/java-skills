"""Chinese message localization helpers for java API standard findings."""

from __future__ import annotations

MESSAGE_TRANSLATIONS = {
    "unified response wrapper is missing": "缺少统一响应包装类",
    "pagination wrapper is missing": "缺少分页响应包装类",
    "error code abstraction is missing": "缺少错误码抽象接口",
    "common error code enum is missing": "缺少通用错误码枚举",
    "global exception handler is missing": "缺少全局异常处理器",
    "catch block handles exception without log.error, rethrow, or onError callback": "catch 块处理异常时缺少 log.error、继续抛出或 onError 回调，可能吞掉异常",
    "normal business failure should not use BusinessException as regular control flow in service/domain/application layer": "正常业务失败不应在 service/domain/application 层通过 BusinessException 作为常规控制流；请使用结果对象、决策对象或 Optional，并在边界转换为统一错误码响应",
    "access log result context is missing": "缺少访问日志结果上下文",
    "global request trace/access log filter is missing": "缺少全局请求追踪/访问日志过滤器",
    "shared CORS configuration is missing": "缺少共享 CORS 配置",
    "shared CORS properties are missing": "缺少共享 CORS 配置属性",
    "request body cache wrapper is missing": "缺少请求体缓存包装器",
    "request body masking policy is missing": "缺少请求体脱敏策略",
    "unified security error response writer is missing": "缺少统一安全错误响应写入器",
    "SQL injection filter registration is missing": "缺少 SQL 注入过滤器注册配置",
    "SQL injection boundary filter is missing": "缺少 SQL 注入边界过滤器",
    "SQL injection guard is missing": "缺少 SQL 注入检测组件",
    "SQL injection properties are missing": "缺少 SQL 注入配置属性",
    "rate limit filter registration is missing": "缺少限流过滤器注册配置",
    "rate limit filter is missing": "缺少限流过滤器",
    "rate limiter contract is missing": "缺少限流器接口",
    "rate limit properties are missing": "缺少限流配置属性",
    "file upload security configuration is missing": "缺少文件上传安全配置",
    "file upload security policy is missing": "缺少文件上传安全策略",
    "file upload security properties are missing": "缺少文件上传安全配置属性",
    "operation audit annotation is missing": "缺少操作审计注解",
    "operation audit aspect is missing": "缺少操作审计切面",
    "operation audit record model is missing": "缺少操作审计记录模型",
    "operation audit service contract is missing": "缺少操作审计服务接口",
    "base entity is missing": "缺少持久化基础实体 BaseEntity",
    "operator context is missing": "缺少操作者上下文 OperatorContext",
    "entity audit fill support is missing": "缺少实体审计字段填充支持",
    "project should document environment configuration in docs/development/configuration_guide.md": "项目应在 docs/development/configuration_guide.md 记录环境配置说明",
    "production secrets should come from environment variables, configuration center, or secret manager placeholders": "生产密钥应来自环境变量、配置中心或密钥管理占位符",
    "生产环境允许凭据时，CORS 不得使用通配 origin": "生产环境允许凭据时，CORS 不得使用通配 origin",
    "production Actuator exposure must not include wildcard endpoints": "生产环境 Actuator 暴露范围不得包含通配端点",
    'ApiResult success code should be the string "000000"': 'ApiResult 成功码应为字符串 "000000"',
    "ErrorCode.code() should return String to preserve 000000 and SMEEEE codes": "ErrorCode.code() 应返回 String，以保留 000000 和 SMEEEE 格式错误码",
    "ErrorCode should not expose httpStatus(); handled business failures use HTTP 200 and body code": "ErrorCode 不要暴露 httpStatus()；已处理业务失败统一使用 HTTP 200，并通过响应体 code 表达结果",
    "ErrorCode should live in common.code; common.error is reserved away from the error code contract": "ErrorCode 应放在 common.code；不要继续放在 common.error 中",
    "ErrorCode.code() still returns int; use String": "ErrorCode.code() 仍返回 int，应改为 String",
    "CommonErrorCode should keep code as String, not numeric status/code": "CommonErrorCode 应将 code 保持为 String，而不是数字状态/编码",
    "CommonErrorCode should not carry httpStatus; keep HTTP status out of business error code contract": "CommonErrorCode 不要携带 httpStatus；HTTP 状态不属于业务错误码契约",
    "CommonErrorCode should live in common.code; common.error is reserved away from the error code contract": "CommonErrorCode 应放在 common.code；不要继续放在 common.error 中",
    "SignatureAuthenticationSupport should read signature from x-sign; authorization is reserved for login token": "SignatureAuthenticationSupport 应从 x-sign 读取签名；authorization 仅保留给登录 token",
    "SignatureAuthenticationSupport should read x-sign-alg and x-api-version": "SignatureAuthenticationSupport 应读取 x-sign-alg 和 x-api-version",
    "ReplayRequestStore should use replaySubject so CMS and SDK can share replay protection": "ReplayRequestStore 应使用 replaySubject，让 CMS 和 SDK 共享防重放组件",
    "ReplayRequestStore should use reqid to match x-reqid": "ReplayRequestStore 应使用 reqid 对应 x-reqid",
    "ReplayRequestStore still uses appId/apiKey; use replaySubject": "ReplayRequestStore 仍在使用 appId/apiKey，应改用 replaySubject",
    "IdempotencyService should use businessType/businessKey from the business request instead of generic idempotencyKey naming": "IdempotencyService 应使用业务请求中的 businessType/businessKey，而不是通用 idempotencyKey 命名",
    "IdempotencyRecord should store the extracted businessKey, not a generic idempotencyKey field": "IdempotencyRecord 应存储提取出的 businessKey，而不是通用 idempotencyKey 字段",
    "OperationAuditAspect should not log raw method arguments by default": "OperationAuditAspect 默认不应记录原始方法参数",
    "admin/CMS API should not use x-api-key as a common request parameter": "admin/CMS API 不应把 x-api-key 作为通用请求参数",
    "security configuration should expose udid-exclude-paths for login/captcha/health endpoints": "安全配置应暴露 udid-exclude-paths，用于登录、验证码、探活接口",
    "security configuration should distinguish auth-exclude-paths from udid-exclude-paths": "安全配置应区分 auth-exclude-paths 和 udid-exclude-paths",
    "security filter should evaluate auth-exclude-paths before udid-exclude-paths": "安全过滤器应先判断 auth-exclude-paths，再判断 udid-exclude-paths",
    "security filter should check x-udid before token or signature authentication unless auth-exclude-paths matched": "除命中 auth-exclude-paths 外，安全过滤器应先检查 x-udid，再进行 token 认证或 x-sign 验签",
    "controller does not appear to return ApiResult<T>": "Controller 看起来没有返回 ApiResult<T>",
    "controller may return a raw or non-standard response type": "Controller 可能返回了原始或非标准响应类型",
    "controller imports entity package; use request/response DTOs instead": "Controller 导入了 entity 包，应改用 request/response DTO",
    "validation message should use an i18n key like {module.field.rule}": "参数校验 message 应使用类似 {module.field.rule} 的 i18n key",
    "repository/mapper must not depend on controller": "repository/mapper 不得依赖 controller",
    "entity must not depend on controller": "entity 不得依赖 controller",
    "entity must not depend on service": "entity 不得依赖 service",
    "common must not depend on business modules": "common 不得依赖业务模块",
    "DTO must not depend on service": "DTO 不得依赖 service",
    "mapper/repository contains ${}; use parameter binding or a server-side allowlist for dynamic fields": "mapper/repository 包含 ${}；动态字段应使用参数绑定或服务端白名单",
    "high-risk transaction API exists but business idempotency service was not found": "存在高风险交易 API，但未找到业务幂等服务",
    "high-risk transaction API exists but replay request store was not found": "存在高风险交易 API，但未找到防重放请求存储",
    "high-risk transaction API exists but signature verification utility was not found": "存在高风险交易 API，但未找到签名验签工具",
}


def localize_message(message: str) -> str:
    if message in MESSAGE_TRANSLATIONS:
        return MESSAGE_TRANSLATIONS[message]

    prefix_replacements = [
        ("deployable module should include ", "可部署模块应包含 "),
        ("production config contains development/test placeholder value ", "生产配置包含开发/测试占位值 "),
        ("ApiResult should expose ", "ApiResult 应暴露 "),
        ("ApiResult contains legacy field ", "ApiResult 包含旧字段 "),
        ("CommonErrorCode should define ", "CommonErrorCode 应定义 "),
        ("SignatureHeaders should define ", "SignatureHeaders 应定义 "),
        ("SignatureHeaders contains obsolete common header ", "SignatureHeaders 包含已废弃的通用请求头 "),
        ("RequestTraceLogFilter should capture ", "RequestTraceLogFilter 应采集 "),
        ("RequestBodyMasker should mask ", "RequestBodyMasker 应脱敏 "),
        ("RequestBodyMasker masks ", "RequestBodyMasker 脱敏了 "),
        ("SecurityErrorResponseWriter should write unified field or log result: ", "SecurityErrorResponseWriter 应写入统一字段或日志结果："),
        ("ApiCorsConfiguration should include ", "ApiCorsConfiguration 应包含 "),
        ("ApiCorsProperties should expose ", "ApiCorsProperties 应暴露 "),
        ("SignatureCanonicalPayload should define ", "SignatureCanonicalPayload 应定义 "),
        ("CmsSecurityFilter should validate CMS signature payload term ", "CmsSecurityFilter 应校验 CMS 签名 payload 契约项 "),
        ("SqlInjectionFilter should include ", "SqlInjectionFilter 应包含 "),
        ("SqlInjectionGuard should include ", "SqlInjectionGuard 应包含 "),
        ("SqlInjectionProperties should expose ", "SqlInjectionProperties 应暴露 "),
        ("RateLimitFilter should include ", "RateLimitFilter 应包含 "),
        ("RateLimitProperties should expose ", "RateLimitProperties 应暴露 "),
        ("InMemoryRateLimiter should include development limiter term ", "InMemoryRateLimiter 应包含开发限流项 "),
        ("FileUploadSecurityPolicy should include ", "FileUploadSecurityPolicy 应包含 "),
        ("FileUploadSecurityProperties should expose ", "FileUploadSecurityProperties 应暴露 "),
        ("SignatureAuthenticationSupport should validate x-sign contract term ", "SignatureAuthenticationSupport 应校验 x-sign 契约项 "),
        ("IdempotencyService should include ", "IdempotencyService 应包含 "),
        ("IdempotencyRecord should include ", "IdempotencyRecord 应包含 "),
        ("OperationAuditAspect should include ", "OperationAuditAspect 应包含 "),
        ("OperationAuditRecord should include ", "OperationAuditRecord 应包含 "),
        ("CMS module exists but ", "存在 CMS 模块，但未找到 "),
        ("SDK module exists but common signature support ", "存在 SDK 模块，但未找到通用签名支持 "),
        ("SDK module exists but ", "存在 SDK 模块，但未找到 "),
        ("BaseEntity should include ", "BaseEntity 应包含 "),
        ("sensitive DTO/entity should not use ", "包含敏感字段的 DTO/entity 不应使用 "),
    ]
    for old, new in prefix_replacements:
        if message.startswith(old):
            translated = new + message[len(old):]
            return translated.removesuffix(" was not found")

    translated = message.replace(" for the standard response envelope", "，用于标准响应包装")
    translated = translated.replace("; use reqid/code/message/ts/data", "；应使用 reqid/code/message/ts/data")
    translated = translated.replace("; standard logs this caller identity field raw by default", "；标准默认以原文记录该调用方身份字段")
    return translated


def localize_finding(finding: Finding) -> Finding:
    return Finding(
        finding.severity,
        finding.rule,
        finding.file,
        finding.line,
        localize_message(finding.message),
    )



def localize_finding(finding, finding_type):
    return finding_type(
        finding.severity,
        finding.rule,
        finding.file,
        finding.line,
        localize_message(finding.message),
    )
