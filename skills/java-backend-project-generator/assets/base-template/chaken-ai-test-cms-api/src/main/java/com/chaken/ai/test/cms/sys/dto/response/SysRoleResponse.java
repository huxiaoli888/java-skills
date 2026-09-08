package com.chaken.ai.test.cms.sys.dto.response;

import com.chaken.ai.test.cms.sys.entity.SysRoleEntity;

public record SysRoleResponse(
        String roleId,
        String roleCode,
        String roleName,
        Integer status,
        String remark) {
    public static SysRoleResponse from(SysRoleEntity entity) {
        return new SysRoleResponse(
                String.valueOf(entity.getId()),
                entity.getRoleCode(),
                entity.getRoleName(),
                entity.getStatus(),
                entity.getRemark());
    }
}
