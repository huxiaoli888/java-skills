package com.chaken.ai.test.cms.security;

public record AdminPrincipal(
        String adminId,
        String username,
        String udid,
        String authType,
        java.util.Set<String> permissions,
        java.util.Set<String> roles) {
    public AdminPrincipal {
        permissions = permissions == null ? java.util.Set.of() : java.util.Set.copyOf(permissions);
        roles = roles == null ? java.util.Set.of() : java.util.Set.copyOf(roles);
    }
}
