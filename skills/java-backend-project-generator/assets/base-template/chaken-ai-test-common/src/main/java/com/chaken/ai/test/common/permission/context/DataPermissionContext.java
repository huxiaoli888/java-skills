package com.chaken.ai.test.common.permission.context;

import com.chaken.ai.test.common.permission.model.DataPermissionScope;
import java.util.Optional;

public final class DataPermissionContext {
    private static final ThreadLocal<DataPermissionScope> CURRENT = new ThreadLocal<>();

    private DataPermissionContext() {
    }

    public static void put(DataPermissionScope scope) {
        CURRENT.set(scope);
    }

    public static Optional<DataPermissionScope> current() {
        return Optional.ofNullable(CURRENT.get());
    }

    public static void clear() {
        CURRENT.remove();
    }
}
