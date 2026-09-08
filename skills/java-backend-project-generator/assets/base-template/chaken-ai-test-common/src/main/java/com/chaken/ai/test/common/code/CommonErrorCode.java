package com.chaken.ai.test.common.code;

public enum CommonErrorCode implements ErrorCode {
    SUCCESS("000000", "common.success", "成功"),
    PARAM_INVALID("AC0001", "common.param.invalid", "请求参数不合法"),
    UNAUTHORIZED("AC0002", "common.unauthorized", "未认证或登录已失效"),
    FORBIDDEN("AC0003", "common.forbidden", "无权访问该资源"),
    RESOURCE_NOT_FOUND("AC0004", "common.resource.not-found", "资源不存在"),
    IDEMPOTENCY_CONFLICT("AC0005", "common.idempotency.conflict", "幂等请求冲突"),
    RATE_LIMITED("AC0006", "common.rate-limited", "请求过于频繁"),
    REQUEST_EXPIRED("AC0007", "common.request.expired", "请求时间戳已过期"),
    REPLAY_REQUEST("AC0008", "common.replay-request", "请求已被重复提交"),
    SIGNATURE_INVALID("AC0009", "common.signature.invalid", "请求签名无效"),
    DUPLICATE_RESOURCE("AC0010", "common.duplicate-resource", "资源已存在"),
    CONCURRENT_MODIFICATION("AC0011", "common.concurrent-modification", "资源已被其他请求修改"),
    SYSTEM_ERROR("AC9999", "common.system-error", "系统异常");

    private final String code;
    private final String messageKey;
    private final String defaultMessage;

    CommonErrorCode(String code, String messageKey, String defaultMessage) {
        this.code = code;
        this.messageKey = messageKey;
        this.defaultMessage = defaultMessage;
    }

    @Override
    public String code() {
        return code;
    }

    @Override
    public String messageKey() {
        return messageKey;
    }

    @Override
    public String defaultMessage() {
        return defaultMessage;
    }
}
