package com.chaken.ai.test.common.security.body;

import com.chaken.ai.test.security.body.CachedBodyHttpServletRequest;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;

import static org.assertj.core.api.Assertions.assertThat;

class CachedBodyHttpServletRequestTest {
    @Test
    void exposesFormParametersFromCachedBody() {
        MockHttpServletRequest request = new MockHttpServletRequest("POST", "/api/v1/cms/form");
        request.setContentType("application/x-www-form-urlencoded; charset=UTF-8");
        byte[] body = "name=tom&name=amy&city=%E4%B8%8A%E6%B5%B7".getBytes(StandardCharsets.UTF_8);

        CachedBodyHttpServletRequest wrappedRequest = new CachedBodyHttpServletRequest(request, body);

        assertThat(wrappedRequest.getParameter("name")).isEqualTo("tom");
        assertThat(wrappedRequest.getParameterValues("name")).containsExactly("tom", "amy");
        assertThat(wrappedRequest.getParameter("city")).isEqualTo("上海");
        assertThat(wrappedRequest.getParameterMap())
                .containsEntry("name", new String[] {"tom", "amy"})
                .containsEntry("city", new String[] {"上海"});
        assertThat(Collections.list(wrappedRequest.getParameterNames()))
                .containsExactlyInAnyOrder("name", "city");
    }
}
