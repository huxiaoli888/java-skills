package com.chaken.ai.test.cms.log.controller;

import com.chaken.ai.test.cms.log.dto.request.OperationLogPageQuery;
import com.chaken.ai.test.cms.log.dto.response.OperationLogResponse;
import com.chaken.ai.test.cms.log.service.OperationLogService;
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
@RequestMapping("/api/v1/cms/logs/operations")
public class CmsOperationLogController {
    private final OperationLogService operationLogService;

    public CmsOperationLogController(OperationLogService operationLogService) {
        this.operationLogService = operationLogService;
    }

    @RequirePermission("sys:log:operation")
    @GetMapping
    public ApiResult<PageResult<OperationLogResponse>> page(@Valid @ModelAttribute OperationLogPageQuery query) {
        return ApiResult.success(operationLogService.page(query), TraceContext.requestId());
    }
}
