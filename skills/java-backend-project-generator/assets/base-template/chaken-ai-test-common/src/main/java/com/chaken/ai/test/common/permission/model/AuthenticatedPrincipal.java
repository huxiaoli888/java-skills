package com.chaken.ai.test.common.permission.model;

import java.util.Set;

public record AuthenticatedPrincipal(
        String principalId,
        String udid,
        String tenantId,
        Set<String> permissions,
        Set<String> roles) {
    public AuthenticatedPrincipal {
        permissions = permissions == null ? Set.of() : Set.copyOf(permissions);
        roles = roles == null ? Set.of() : Set.copyOf(roles);
    }
}
