package com.chaken.ai.test.common.permission.service;

import com.chaken.ai.test.common.permission.model.AuthenticatedPrincipal;
import java.util.Arrays;
import java.util.Set;

public class DefaultPermissionEvaluator implements PermissionEvaluator {
    private static final String WILDCARD = "*";

    @Override
    public boolean hasPermission(AuthenticatedPrincipal principal, String[] permissions, boolean any) {
        if (principal == null || permissions == null || permissions.length == 0) {
            return false;
        }
        Set<String> owned = principal.permissions();
        if (owned.contains(WILDCARD)) {
            return true;
        }
        return any
                ? Arrays.stream(permissions).anyMatch(owned::contains)
                : Arrays.stream(permissions).allMatch(owned::contains);
    }
}
