package com.chaken.ai.test.common.api;

import com.chaken.ai.test.common.trace.AccessLogContext;

public class ApiResult<T> {
    private String reqid;
    private String code;
    private String message;
    private long ts = System.currentTimeMillis();
    private T data;

    public ApiResult() {
    }

    private ApiResult(String reqid, String code, String message, T data) {
        this.reqid = reqidOrEmpty(reqid);
        this.code = code;
        this.message = message;
        this.data = data;
        AccessLogContext.setResult(code, message);
    }

    public static <T> ApiResult<T> success(T data, String reqid) {
        return new ApiResult<>(reqid, "000000", "成功", data);
    }

    public static <T> ApiResult<T> fail(String code, String message, String reqid) {
        return new ApiResult<>(reqid, code, message, null);
    }

    public static <T> ApiResult<T> fail(String code, String message, T data, String reqid) {
        return new ApiResult<>(reqid, code, message, data);
    }

    public String getReqid() {
        return reqid;
    }

    public void setReqid(String reqid) {
        this.reqid = reqidOrEmpty(reqid);
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public long getTs() {
        return ts;
    }

    public void setTs(long ts) {
        this.ts = ts;
    }

    public T getData() {
        return data;
    }

    public void setData(T data) {
        this.data = data;
    }

    private static String reqidOrEmpty(String reqid) {
        return reqid == null ? "" : reqid;
    }
}
