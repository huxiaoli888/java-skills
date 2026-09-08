package com.chaken.ai.test.common.api;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;

class ApiResultTest {

    @Test
    void nullReqidShouldRenderAsEmptyString() {
        ApiResult<Object> result = ApiResult.fail("AC0001", "参数错误", null);

        assertThat(result.getReqid()).isEmpty();

        result.setReqid(null);

        assertThat(result.getReqid()).isEmpty();
    }
}
