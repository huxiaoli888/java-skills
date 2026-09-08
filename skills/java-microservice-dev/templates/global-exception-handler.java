package {{basePackage}}.exception;

import javax.servlet.http.HttpServletRequest;
import javax.validation.ConstraintViolationException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.MissingRequestHeaderException;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import {{basePackage}}.exception.CommonErrorCode;
import {{basePackage}}.web.ApiResponse;

@RestControllerAdvice
public class GlobalExceptionHandler {
    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ApiResponse<Void> handleValidation(MethodArgumentNotValidException ex, HttpServletRequest request) {
        return ApiResponse.error(CommonErrorCode.PARAM_INVALID, reqidOrEmpty(request));
    }

    @ExceptionHandler(ConstraintViolationException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ApiResponse<Void> handleConstraintViolation(ConstraintViolationException ex, HttpServletRequest request) {
        return ApiResponse.error(CommonErrorCode.PARAM_INVALID, reqidOrEmpty(request));
    }

    @ExceptionHandler(MissingRequestHeaderException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ApiResponse<Void> handleMissingRequestHeader(MissingRequestHeaderException ex, HttpServletRequest request) {
        return ApiResponse.error(CommonErrorCode.PARAM_INVALID, reqidOrEmpty(request));
    }

    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ApiResponse<Void> handleException(Exception ex, HttpServletRequest request) {
        String reqid = reqidOrEmpty(request);
        log.error("未预期异常 reqid={}", reqid, ex);
        return ApiResponse.error(CommonErrorCode.SYSTEM_ERROR, reqid);
    }

    private static String reqidOrEmpty(HttpServletRequest request) {
        if (request == null) {
            return "";
        }
        String reqid = request.getHeader("x-reqid");
        return reqid == null ? "" : reqid;
    }
}
