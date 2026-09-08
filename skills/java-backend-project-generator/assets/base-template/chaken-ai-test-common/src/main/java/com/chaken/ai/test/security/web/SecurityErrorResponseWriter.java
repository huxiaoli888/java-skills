package com.chaken.ai.test.security.web;

import com.chaken.ai.test.common.code.CommonErrorCode;
import com.chaken.ai.test.common.trace.AccessLogContext;
import com.chaken.ai.test.common.trace.TraceContext;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import org.springframework.http.MediaType;

public final class SecurityErrorResponseWriter {
    private SecurityErrorResponseWriter() {
    }

    public static void write(HttpServletResponse response, CommonErrorCode errorCode) throws IOException {
        AccessLogContext.setResult(errorCode.code(), errorCode.defaultMessage());
        response.setStatus(HttpServletResponse.SC_OK);
        response.setCharacterEncoding(StandardCharsets.UTF_8.name());
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        response.getWriter().write("{"
                + "\"reqid\":\"" + json(TraceContext.requestId()) + "\","
                + "\"code\":\"" + json(errorCode.code()) + "\","
                + "\"message\":\"" + json(errorCode.defaultMessage()) + "\","
                + "\"ts\":" + System.currentTimeMillis() + ","
                + "\"data\":null"
                + "}");
    }

    private static String json(String value) {
        if (value == null) {
            return "";
        }
        return value
                .replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\r", "\\r")
                .replace("\n", "\\n");
    }
}
