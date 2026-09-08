package com.chaken.ai.test.common.trace;

public final class AccessLogContext {
    private static final ThreadLocal<Result> RESULT = new ThreadLocal<>();

    private AccessLogContext() {
    }

    public static void setResult(String code, String message) {
        RESULT.set(new Result(value(code), value(message)));
    }

    public static Result resultOrDefault(int statusCode) {
        Result result = RESULT.get();
        if (result != null) {
            return result;
        }
        if (statusCode >= 200 && statusCode < 300) {
            return new Result("000000", "成功");
        }
        return new Result("HTTP_" + statusCode, "http status " + statusCode);
    }

    public static void clear() {
        RESULT.remove();
    }

    private static String value(String value) {
        return value == null ? "" : value;
    }

    public record Result(String code, String message) {
    }
}
