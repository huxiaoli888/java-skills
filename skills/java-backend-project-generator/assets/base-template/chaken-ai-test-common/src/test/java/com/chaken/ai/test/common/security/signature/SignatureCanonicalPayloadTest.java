package com.chaken.ai.test.common.security.signature;

import com.chaken.ai.test.security.signature.SignatureCanonicalPayload;
import java.nio.charset.StandardCharsets;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;

import static org.assertj.core.api.Assertions.assertThat;

class SignatureCanonicalPayloadTest {
    @Test
    void canonicalizesGetQueryByDecodedKeyAndValue() {
        MockHttpServletRequest request = new MockHttpServletRequest("GET", "/api/v1/sdk/tasks");
        request.setQueryString("b=2&a=2&a=1");

        assertThat(SignatureCanonicalPayload.query(request)).isEqualTo("a=1&a=2&b=2");
    }

    @Test
    void keepsJsonBodyAsRawBytes() {
        MockHttpServletRequest request = new MockHttpServletRequest("POST", "/api/v1/sdk/tasks");
        request.setContentType("application/json; charset=UTF-8");
        byte[] rawBody = "{\"b\":2,\"a\":1}".getBytes(StandardCharsets.UTF_8);

        assertThat(SignatureCanonicalPayload.body(request, rawBody)).isSameAs(rawBody);
    }

    @Test
    void keepsCmsFormBodyAsRawBytesWhenSupported() {
        MockHttpServletRequest request = new MockHttpServletRequest("POST", "/api/v1/cms/tasks");
        request.setContentType("application/x-www-form-urlencoded; charset=UTF-8");
        byte[] rawBody = "name=tom&age=18&name=amy".getBytes(StandardCharsets.UTF_8);

        assertThat(SignatureCanonicalPayload.body(request, rawBody)).isSameAs(rawBody);
    }

    @Test
    void sdkDoesNotCanonicalizeFormBody() {
        MockHttpServletRequest request = new MockHttpServletRequest("POST", "/api/v1/sdk/tasks");
        request.setContentType("application/x-www-form-urlencoded; charset=UTF-8");
        byte[] rawBody = "b=2&a=1".getBytes(StandardCharsets.UTF_8);

        assertThat(SignatureCanonicalPayload.body(request, rawBody)).isSameAs(rawBody);
    }
}
