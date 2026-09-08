package com.chaken.ai.test.cms.log.controller;

import com.chaken.ai.test.cms.log.dto.request.LoginLogPageQuery;
import com.chaken.ai.test.cms.log.dto.response.LoginLogResponse;
import com.chaken.ai.test.cms.log.service.LoginLogService;
import com.chaken.ai.test.common.api.ApiResult;
import com.chaken.ai.test.common.api.PageResult;
import com.chaken.ai.test.common.permission.annotation.RequirePermission;
import com.chaken.ai.test.common.trace.TraceContext;
import jakarta.validation.Valid;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@Validated
@RestController
@RequestMapping("/api/v1/cms/logs/logins")
public class CmsLoginLogController {
    private final LoginLogService loginLogService;

    public CmsLoginLogController(LoginLogService loginLogService) {
        this.loginLogService = loginLogService;
    }

    @RequirePermission("sys:log:login")
    @GetMapping
    public ApiResult<PageResult<LoginLogResponse>> page(@Valid @ModelAttribute LoginLogPageQuery query) {
        return ApiResult.success(loginLogService.page(query), TraceContext.requestId());
    }
}
