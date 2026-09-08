package com.chaken.ai.test.cms.sys.dto.response;

import com.chaken.ai.test.cms.sys.entity.SysMenuEntity;

public record SysMenuResponse(
        String menuId,
        String parentId,
        String menuName,
        String menuType,
        String path,
        String permissionCode,
        Integer sortNo,
        Integer status) {
    public static SysMenuResponse from(SysMenuEntity entity) {
        return new SysMenuResponse(
                String.valueOf(entity.getId()),
                entity.getParentId() == null ? "" : String.valueOf(entity.getParentId()),
                entity.getMenuName(),
                entity.getMenuType(),
                entity.getPath(),
                entity.getPermissionCode(),
                entity.getSortNo(),
                entity.getStatus());
    }
}
