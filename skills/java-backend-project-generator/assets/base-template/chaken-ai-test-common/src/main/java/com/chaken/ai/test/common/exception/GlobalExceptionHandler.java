package com.chaken.ai.test.common.exception;

import com.chaken.ai.test.common.api.ApiResult;
import com.chaken.ai.test.common.code.CommonErrorCode;
import com.chaken.ai.test.common.code.ErrorCode;
import com.chaken.ai.test.common.trace.TraceContext;
import jakarta.validation.ConstraintViolationException;
import java.util.List;
import java.util.Locale;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.MessageSource;
import org.springframework.context.i18n.LocaleContextHolder;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.MissingRequestHeaderException;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;

@RestControllerAdvice
public class GlobalExceptionHandler {
    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);
    private final MessageSource messageSource;

    public GlobalExceptionHandler(MessageSource messageSource) {
        this.messageSource = messageSource;
    }

    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ApiResult<Void>> handleBusinessException(BusinessException ex) {
        String message = messageFor(ex.getErrorCode(), ex.getMessage());
        return ResponseEntity.ok(ApiResult.fail(
                ex.getErrorCode().code(),
                message,
                TraceContext.requestId()));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResult<List<FieldErrorItem>>> handleValidationException(MethodArgumentNotValidException ex) {
        List<FieldErrorItem> errors = ex.getBindingResult()
                .getFieldErrors()
                .stream()
                .map(this::toFieldErrorItem)
                .collect(Collectors.toList());

        return ResponseEntity.ok(ApiResult.fail(
                CommonErrorCode.PARAM_INVALID.code(),
                CommonErrorCode.PARAM_INVALID.defaultMessage(),
                errors,
                TraceContext.requestId()));
    }

    @ExceptionHandler({
            ConstraintViolationException.class,
            HttpMessageNotReadableException.class,
            MethodArgumentTypeMismatchException.class,
            MissingRequestHeaderException.class,
            MissingServletRequestParameterException.class
    })
    public ResponseEntity<ApiResult<Void>> handleBadRequest(Exception ex) {
        return ResponseEntity.ok(ApiResult.fail(
                CommonErrorCode.PARAM_INVALID.code(),
                CommonErrorCode.PARAM_INVALID.defaultMessage(),
                TraceContext.requestId()));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResult<Void>> handleException(Exception ex) {
        log.error("未预期异常 reqid={}", TraceContext.requestId(), ex);
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(ApiResult.fail(
                CommonErrorCode.SYSTEM_ERROR.code(),
                CommonErrorCode.SYSTEM_ERROR.defaultMessage(),
                TraceContext.requestId()));
    }

    private FieldErrorItem toFieldErrorItem(FieldError error) {
        return new FieldErrorItem(
                error.getField(),
                error.getDefaultMessage(),
                error.getCode(),
                maskRejectedValue(error.getRejectedValue()));
    }

    private Object maskRejectedValue(Object rejectedValue) {
        if (rejectedValue == null) {
            return null;
        }
        String value = String.valueOf(rejectedValue);
        if (value.length() <= 2) {
            return "***";
        }
        return value.substring(0, 1) + "***" + value.substring(value.length() - 1);
    }

    private String messageFor(ErrorCode errorCode, String fallback) {
        Locale locale = LocaleContextHolder.getLocale();
        return messageSource.getMessage(errorCode.messageKey(), null, fallback, locale);
    }
}
