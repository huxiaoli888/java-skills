package com.chaken.ai.test.cms.auth.controller;

import com.chaken.ai.test.cms.auth.dto.request.CmsLoginRequest;
import com.chaken.ai.test.cms.auth.dto.response.CmsLoginResponse;
import com.chaken.ai.test.cms.auth.service.CmsAuthService;
import com.chaken.ai.test.common.api.ApiResult;
import com.chaken.ai.test.common.result.ServiceResult;
import com.chaken.ai.test.common.trace.TraceContext;
import com.chaken.ai.test.security.signature.SignatureHeaders;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/cms/auth")
public class CmsAuthController {
    private final CmsAuthService authService;

    public CmsAuthController(CmsAuthService authService) {
        this.authService = authService;
    }

    @PostMapping("/login")
    public ResponseEntity<ApiResult<CmsLoginResponse>> login(
            @Valid @RequestBody CmsLoginRequest request,
            HttpServletRequest httpRequest) {
        ServiceResult<CmsLoginResponse> result = authService.login(request, httpRequest);
        if (result.isSuccess()) {
            return ResponseEntity.ok(ApiResult.success(result.data(), TraceContext.requestId()));
        }
        return ResponseEntity.ok(ApiResult.<CmsLoginResponse>fail(
                result.errorCode().code(),
                result.errorCode().defaultMessage(),
                TraceContext.requestId()));
    }

    @PostMapping("/logout")
    public ApiResult<Void> logout(
            @RequestHeader(SignatureHeaders.AUTHORIZATION) String authorization,
            HttpServletRequest httpRequest) {
        authService.logout(authorization, httpRequest);
        return ApiResult.success(null, TraceContext.requestId());
    }
}
