package com.chaken.ai.test.cms.sys.controller;

import com.chaken.ai.test.cms.sys.dto.request.SysDictPageQuery;
import com.chaken.ai.test.cms.sys.dto.response.SysDictItemResponse;
import com.chaken.ai.test.cms.sys.dto.response.SysDictResponse;
import com.chaken.ai.test.cms.sys.service.SysDictService;
import com.chaken.ai.test.common.api.ApiResult;
import com.chaken.ai.test.common.api.PageResult;
import com.chaken.ai.test.common.permission.annotation.RequirePermission;
import com.chaken.ai.test.common.trace.TraceContext;
import jakarta.validation.Valid;
import java.util.List;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@Validated
@RestController
@RequestMapping("/api/v1/cms/sys/dicts")
public class CmsSysDictController {
    private final SysDictService dictService;

    public CmsSysDictController(SysDictService dictService) {
        this.dictService = dictService;
    }

    @RequirePermission("sys:dict:list")
    @GetMapping
    public ApiResult<PageResult<SysDictResponse>> page(@Valid @ModelAttribute SysDictPageQuery query) {
        return ApiResult.success(dictService.page(query), TraceContext.requestId());
    }

    @RequirePermission("sys:dict:list")
    @GetMapping("/{dictCode}/items")
    public ApiResult<List<SysDictItemResponse>> listItems(@PathVariable String dictCode) {
        return ApiResult.success(dictService.listItems(dictCode), TraceContext.requestId());
    }
}
