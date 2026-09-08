package com.chaken.ai.test.common.trace;

import org.slf4j.MDC;

public final class TraceContext {
    public static final String TRACE_ID = "traceId";
    public static final String REQUEST_ID = "requestId";

    private TraceContext() {
    }

    public static String traceId() {
        return MDC.get(TRACE_ID);
    }

    public static String requestId() {
        return MDC.get(REQUEST_ID);
    }

    public static void put(String traceId, String requestId) {
        MDC.put(TRACE_ID, traceId);
        if (requestId != null && !requestId.isEmpty()) {
            MDC.put(REQUEST_ID, requestId);
        }
    }

    public static void clear() {
        MDC.remove(TRACE_ID);
        MDC.remove(REQUEST_ID);
    }
}
