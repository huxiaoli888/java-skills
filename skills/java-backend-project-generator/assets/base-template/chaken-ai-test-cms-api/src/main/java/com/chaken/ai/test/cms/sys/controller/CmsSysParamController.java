package com.chaken.ai.test.cms.sys.controller;

import com.chaken.ai.test.cms.sys.dto.request.SysParamPageQuery;
import com.chaken.ai.test.cms.sys.dto.response.SysParamResponse;
import com.chaken.ai.test.cms.sys.service.SysParamService;
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
@RequestMapping("/api/v1/cms/sys/params")
public class CmsSysParamController {
    private final SysParamService paramService;

    public CmsSysParamController(SysParamService paramService) {
        this.paramService = paramService;
    }

    @RequirePermission("sys:param:list")
    @GetMapping
    public ApiResult<PageResult<SysParamResponse>> page(@Valid @ModelAttribute SysParamPageQuery query) {
        return ApiResult.success(paramService.page(query), TraceContext.requestId());
    }
}
