package com.chaken.ai.test.cms.sys.controller;

import com.chaken.ai.test.cms.sys.dto.request.SysUserPageQuery;
import com.chaken.ai.test.cms.sys.dto.response.SysUserResponse;
import com.chaken.ai.test.cms.sys.service.SysUserService;
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
@RequestMapping("/api/v1/cms/sys/users")
public class CmsSysUserController {
    private final SysUserService userService;

    public CmsSysUserController(SysUserService userService) {
        this.userService = userService;
    }

    @RequirePermission("sys:user:list")
    @GetMapping
    public ApiResult<PageResult<SysUserResponse>> page(@Valid @ModelAttribute SysUserPageQuery query) {
        return ApiResult.success(userService.page(query), TraceContext.requestId());
    }
}
