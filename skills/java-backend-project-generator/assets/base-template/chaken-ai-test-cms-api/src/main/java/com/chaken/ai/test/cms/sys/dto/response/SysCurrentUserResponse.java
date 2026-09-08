package com.chaken.ai.test.cms.sys.dto.response;

import java.util.List;

public record SysCurrentUserResponse(
        String userId,
        String username,
        String displayName,
        Boolean superAdmin,
        List<String> roles,
        List<String> permissions,
        List<SysMenuResponse> menus) {
}
