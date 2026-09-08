package com.chaken.ai.test.common.persistence;

public final class OperatorContext {
    private static final ThreadLocal<String> OPERATOR_ID = new ThreadLocal<>();

    private OperatorContext() {
    }

    public static void put(String operatorId) {
        if (operatorId != null && !operatorId.isBlank()) {
            OPERATOR_ID.set(operatorId);
        }
    }

    public static String operatorId() {
        return OPERATOR_ID.get();
    }

    public static void clear() {
        OPERATOR_ID.remove();
    }
}
