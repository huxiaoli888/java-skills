package com.chaken.ai.test.cms.sys.controller;

import com.chaken.ai.test.cms.sys.dto.response.SysRoleResponse;
import com.chaken.ai.test.cms.sys.service.SysRoleService;
import com.chaken.ai.test.common.api.ApiResult;
import com.chaken.ai.test.common.permission.annotation.RequirePermission;
import com.chaken.ai.test.common.trace.TraceContext;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/cms/sys/roles")
public class CmsSysRoleController {
    private final SysRoleService roleService;

    public CmsSysRoleController(SysRoleService roleService) {
        this.roleService = roleService;
    }

    @RequirePermission("sys:role:list")
    @GetMapping
    public ApiResult<List<SysRoleResponse>> list() {
        return ApiResult.success(roleService.listActiveRoles(), TraceContext.requestId());
    }
}
