package com.chaken.ai.test.security.signature;

import com.chaken.ai.test.common.code.CommonErrorCode;

public class SignatureAuthenticationException extends RuntimeException {
    private final CommonErrorCode errorCode;

    public SignatureAuthenticationException(CommonErrorCode errorCode) {
        super(errorCode.defaultMessage());
        this.errorCode = errorCode;
    }

    public CommonErrorCode errorCode() {
        return errorCode;
    }
}
