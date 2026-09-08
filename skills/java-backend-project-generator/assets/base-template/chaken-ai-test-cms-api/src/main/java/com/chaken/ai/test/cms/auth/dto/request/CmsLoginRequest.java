package com.chaken.ai.test.cms.auth.dto.request;

import jakarta.validation.constraints.NotBlank;

public record CmsLoginRequest(
        @NotBlank String username,
        @NotBlank String password) {
}
