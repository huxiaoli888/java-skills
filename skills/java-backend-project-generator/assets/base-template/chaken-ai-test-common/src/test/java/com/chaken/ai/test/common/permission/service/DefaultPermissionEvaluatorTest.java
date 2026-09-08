package com.chaken.ai.test.common.permission.service;

import static org.assertj.core.api.Assertions.assertThat;

import com.chaken.ai.test.common.permission.model.AuthenticatedPrincipal;
import java.util.Set;
import org.junit.jupiter.api.Test;

class DefaultPermissionEvaluatorTest {
    private final DefaultPermissionEvaluator evaluator = new DefaultPermissionEvaluator();

    @Test
    void requiresAllPermissionsByDefault() {
        AuthenticatedPrincipal principal = new AuthenticatedPrincipal(
                "admin",
                "udid-1",
                "tenant-1",
                Set.of("system:user:create", "system:user:update"),
                Set.of("ADMIN"));

        assertThat(evaluator.hasPermission(
                principal,
                new String[] {"system:user:create", "system:user:update"},
                false)).isTrue();
        assertThat(evaluator.hasPermission(
                principal,
                new String[] {"system:user:create", "system:user:delete"},
                false)).isFalse();
    }

    @Test
    void supportsAnyPermissionAndWildcard() {
        AuthenticatedPrincipal principal = new AuthenticatedPrincipal(
                "admin",
                "udid-1",
                "tenant-1",
                Set.of("system:user:create"),
                Set.of("ADMIN"));
        AuthenticatedPrincipal superAdmin = new AuthenticatedPrincipal(
                "root",
                "udid-2",
                "tenant-1",
                Set.of("*"),
                Set.of("SUPER_ADMIN"));

        assertThat(evaluator.hasPermission(
                principal,
                new String[] {"system:user:create", "system:user:delete"},
                true)).isTrue();
        assertThat(evaluator.hasPermission(
                superAdmin,
                new String[] {"system:role:grant"},
                false)).isTrue();
    }
}
