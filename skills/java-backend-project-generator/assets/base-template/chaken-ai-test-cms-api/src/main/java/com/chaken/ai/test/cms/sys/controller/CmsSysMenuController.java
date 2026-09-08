package com.chaken.ai.test.cms.sys.controller;

import com.chaken.ai.test.cms.sys.dto.response.SysMenuResponse;
import com.chaken.ai.test.cms.sys.service.SysMenuService;
import com.chaken.ai.test.common.api.ApiResult;
import com.chaken.ai.test.common.permission.annotation.RequirePermission;
import com.chaken.ai.test.common.trace.TraceContext;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/cms/sys/menus")
public class CmsSysMenuController {
    private final SysMenuService menuService;

    public CmsSysMenuController(SysMenuService menuService) {
        this.menuService = menuService;
    }

    @RequirePermission("sys:menu:list")
    @GetMapping
    public ApiResult<List<SysMenuResponse>> list() {
        return ApiResult.success(menuService.listActiveMenus(), TraceContext.requestId());
    }
}
