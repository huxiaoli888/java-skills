package com.chaken.ai.test.common.permission.context;

import static org.assertj.core.api.Assertions.assertThat;

import com.chaken.ai.test.common.permission.model.AuthenticatedPrincipal;
import com.chaken.ai.test.common.permission.model.DataPermissionScope;
import java.util.Set;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;

class PrincipalContextTest {
    @AfterEach
    void clearContext() {
        PrincipalContext.clear();
        TenantContext.clear();
        DataPermissionContext.clear();
    }

    @Test
    void storesPrincipalTenantAndDataScopeForCurrentRequest() {
        PrincipalContext.put(new AuthenticatedPrincipal(
                "admin",
                "udid-1",
                "tenant-1",
                Set.of("system:user:page"),
                Set.of("ADMIN")));
        TenantContext.put("tenant-1");
        DataPermissionContext.put(new DataPermissionScope("tenant-1", Set.of("org-1"), false));

        assertThat(PrincipalContext.principalId()).isEqualTo("admin");
        assertThat(TenantContext.current()).contains("tenant-1");
        assertThat(DataPermissionContext.current().orElseThrow().organizationIds()).containsExactly("org-1");
    }
}
