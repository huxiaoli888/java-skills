package com.chaken.ai.test.common.result;

import com.chaken.ai.test.common.code.ErrorCode;

public class ServiceResult<T> {
    private final T data;
    private final ErrorCode errorCode;

    private ServiceResult(T data, ErrorCode errorCode) {
        this.data = data;
        this.errorCode = errorCode;
    }

    public static <T> ServiceResult<T> success(T data) {
        return new ServiceResult<>(data, null);
    }

    public static <T> ServiceResult<T> failure(ErrorCode errorCode) {
        return new ServiceResult<>(null, errorCode);
    }

    public boolean isSuccess() {
        return errorCode == null;
    }

    public T data() {
        return data;
    }

    public ErrorCode errorCode() {
        return errorCode;
    }
}
