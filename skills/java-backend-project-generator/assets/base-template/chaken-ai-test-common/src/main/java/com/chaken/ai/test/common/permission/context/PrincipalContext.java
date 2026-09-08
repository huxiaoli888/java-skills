package com.chaken.ai.test.common.permission.context;

import com.chaken.ai.test.common.permission.model.AuthenticatedPrincipal;
import java.util.Optional;

public final class PrincipalContext {
    private static final ThreadLocal<AuthenticatedPrincipal> CURRENT = new ThreadLocal<>();

    private PrincipalContext() {
    }

    public static void put(AuthenticatedPrincipal principal) {
        CURRENT.set(principal);
    }

    public static Optional<AuthenticatedPrincipal> current() {
        return Optional.ofNullable(CURRENT.get());
    }

    public static String principalId() {
        return current().map(AuthenticatedPrincipal::principalId).orElse("");
    }

    public static void clear() {
        CURRENT.remove();
    }
}
