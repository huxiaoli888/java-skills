package com.chaken.ai.test.common.permission.model;

import java.util.Set;

public record DataPermissionScope(
        String tenantId,
        Set<String> organizationIds,
        boolean onlySelf) {
    public DataPermissionScope {
        organizationIds = organizationIds == null ? Set.of() : Set.copyOf(organizationIds);
    }

    public static DataPermissionScope allForTenant(String tenantId) {
        return new DataPermissionScope(tenantId, Set.of(), false);
    }
}
