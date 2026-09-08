package {{basePackage}}.web;

import {{basePackage}}.exception.CommonErrorCode;
import {{basePackage}}.exception.ErrorCode;

public class ApiResponse<T> {
    private String reqid;
    private String code;
    private String message;
    private long ts;
    private T data;

    public static <T> ApiResponse<T> success(T data, String reqid) {
        ApiResponse<T> response = new ApiResponse<>();
        response.reqid = reqidOrEmpty(reqid);
        response.code = CommonErrorCode.SUCCESS.code();
        response.message = CommonErrorCode.SUCCESS.defaultMessage();
        response.ts = System.currentTimeMillis();
        response.data = data;
        return response;
    }

    public static <T> ApiResponse<T> error(ErrorCode errorCode, String reqid) {
        ApiResponse<T> response = new ApiResponse<>();
        response.reqid = reqidOrEmpty(reqid);
        response.code = errorCode.code();
        response.message = errorCode.defaultMessage();
        response.ts = System.currentTimeMillis();
        return response;
    }

    public String getReqid() {
        return reqid;
    }

    public String getCode() {
        return code;
    }

    public String getMessage() {
        return message;
    }

    public long getTs() {
        return ts;
    }

    public T getData() {
        return data;
    }

    private static String reqidOrEmpty(String reqid) {
        return reqid == null ? "" : reqid;
    }
}
