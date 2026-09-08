package com.chaken.ai.test.cms.auth.dto.response;

import java.time.Instant;

public record CmsLoginResponse(
        String token,
        Instant expireTime,
        String adminId,
        String username) {
}
