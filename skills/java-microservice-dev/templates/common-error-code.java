package {{basePackage}}.exception;

public enum CommonErrorCode implements ErrorCode {
    SUCCESS("000000", "成功", 200),
    PARAM_INVALID("AC0001", "请求参数不合法", 400),
    SYSTEM_ERROR("AC9999", "系统异常", 500);

    private final String code;
    private final String defaultMessage;
    private final int httpStatus;

    CommonErrorCode(String code, String defaultMessage, int httpStatus) {
        this.code = code;
        this.defaultMessage = defaultMessage;
        this.httpStatus = httpStatus;
    }

    @Override
    public String code() {
        return code;
    }

    @Override
    public String defaultMessage() {
        return defaultMessage;
    }

    @Override
    public int httpStatus() {
        return httpStatus;
    }
}
