package com.chaken.ai.test.common.trace;

import com.chaken.ai.test.common.logging.RequestBodyMasker;
import com.chaken.ai.test.common.persistence.OperatorContext;
import com.chaken.ai.test.security.body.CachedBodyHttpServletRequest;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.util.StreamUtils;
import org.springframework.web.filter.OncePerRequestFilter;

public class RequestTraceLogFilter extends OncePerRequestFilter {
    public static final String TRACE_ID_HEADER = "x-trace-id";
    public static final String REQUEST_ID_HEADER = "x-reqid";
    private static final Logger log = LoggerFactory.getLogger(RequestTraceLogFilter.class);
    private static final String API_KEY_HEADER = "x-api-key";
    private static final String UDID_HEADER = "x-udid";
    private final RequestBodyMasker requestBodyMasker = RequestBodyMasker.defaultMasker();

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        Instant requestTime = Instant.now();
        long start = System.currentTimeMillis();
        String traceId = firstNonBlank(request.getHeader(TRACE_ID_HEADER), UUID.randomUUID().toString());
        String requestId = request.getHeader(REQUEST_ID_HEADER);
        byte[] requestBody = StreamUtils.copyToByteArray(request.getInputStream());
        CachedBodyHttpServletRequest wrappedRequest = new CachedBodyHttpServletRequest(request, requestBody);
        TraceContext.put(traceId, requestId);
        OperatorContext.put(firstNonBlank(request.getHeader(UDID_HEADER), request.getHeader(API_KEY_HEADER)));
        response.setHeader(TRACE_ID_HEADER, traceId);
        try {
            filterChain.doFilter(wrappedRequest, response);
        } finally {
            Instant responseTime = Instant.now();
            long durationMs = System.currentTimeMillis() - start;
            AccessLogContext.Result result = AccessLogContext.resultOrDefault(response.getStatus());
            log.info(
                    "access reqid={} traceId={} method={} path={} status={} code={} message={} requestTime={} responseTime={} durationMs={} clientIp={} udid={} apiKey={} requestBody={}",
                    TraceContext.requestId(),
                    TraceContext.traceId(),
                    wrappedRequest.getMethod(),
                    wrappedRequest.getRequestURI(),
                    response.getStatus(),
                    result.code(),
                    result.message(),
                    requestTime,
                    responseTime,
                    durationMs,
                    clientIp(wrappedRequest),
                    headerValue(wrappedRequest.getHeader(UDID_HEADER)),
                    headerValue(wrappedRequest.getHeader(API_KEY_HEADER)),
                    requestBody(requestBody, wrappedRequest.getCharacterEncoding()));
            AccessLogContext.clear();
            OperatorContext.clear();
            TraceContext.clear();
        }
    }

    private String firstNonBlank(String value, String fallback) {
        return value == null || value.trim().isEmpty() ? fallback : value;
    }

    private String clientIp(HttpServletRequest request) {
        String forwardedFor = request.getHeader("x-forwarded-for");
        if (forwardedFor != null && !forwardedFor.isBlank()) {
            return forwardedFor.split(",")[0].trim();
        }
        return request.getRemoteAddr();
    }

    private String headerValue(String value) {
        return value == null ? "" : value;
    }

    private String requestBody(byte[] body, String encoding) {
        if (body == null || body.length == 0) {
            return "";
        }
        Charset charset = encoding == null ? StandardCharsets.UTF_8 : Charset.forName(encoding);
        String rawBody = new String(body, charset);
        return requestBodyMasker.mask(rawBody)
                .replace("\\", "\\\\")
                .replace("\r", "\\r")
                .replace("\n", "\\n");
    }
}
