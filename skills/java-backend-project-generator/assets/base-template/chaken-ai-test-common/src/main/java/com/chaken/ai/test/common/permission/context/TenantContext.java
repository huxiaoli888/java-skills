package com.chaken.ai.test.common.permission.context;

import java.util.Optional;

public final class TenantContext {
    private static final ThreadLocal<String> CURRENT = new ThreadLocal<>();

    private TenantContext() {
    }

    public static void put(String tenantId) {
        CURRENT.set(tenantId);
    }

    public static Optional<String> current() {
        return Optional.ofNullable(CURRENT.get());
    }

    public static void clear() {
        CURRENT.remove();
    }
}
