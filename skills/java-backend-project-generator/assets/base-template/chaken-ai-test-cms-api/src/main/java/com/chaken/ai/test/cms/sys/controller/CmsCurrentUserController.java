package com.chaken.ai.test.cms.sys.controller;

import com.chaken.ai.test.cms.sys.dto.response.SysCurrentUserResponse;
import com.chaken.ai.test.cms.sys.service.SysUserService;
import com.chaken.ai.test.common.api.ApiResult;
import com.chaken.ai.test.common.trace.TraceContext;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/cms/sys/current-user")
public class CmsCurrentUserController {
    private final SysUserService userService;

    public CmsCurrentUserController(SysUserService userService) {
        this.userService = userService;
    }

    @GetMapping
    public ApiResult<SysCurrentUserResponse> currentUser() {
        return ApiResult.success(userService.currentUser(), TraceContext.requestId());
    }
}
