package com.chaken.ai.test.common.exception;

import com.chaken.ai.test.common.code.CommonErrorCode;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

class GlobalExceptionHandlerContractTest {
    @Test
    void businessExceptionShouldCarryStableErrorCode() {
        BusinessException exception = new BusinessException(CommonErrorCode.PARAM_INVALID);

        assertThat(exception.getErrorCode().code()).isEqualTo("AC0001");
        assertThat(exception.getErrorCode().defaultMessage()).isEqualTo("请求参数不合法");
    }
}
