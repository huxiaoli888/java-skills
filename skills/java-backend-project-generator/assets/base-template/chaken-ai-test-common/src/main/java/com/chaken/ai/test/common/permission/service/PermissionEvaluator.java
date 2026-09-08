package com.chaken.ai.test.common.permission.service;

import com.chaken.ai.test.common.permission.model.AuthenticatedPrincipal;

public interface PermissionEvaluator {
    boolean hasPermission(AuthenticatedPrincipal principal, String[] permissions, boolean any);
}
