package com.chaken.ai.test.cms.sys.dto.response;

import com.chaken.ai.test.cms.sys.entity.SysUserEntity;
import java.time.Instant;

public record SysUserResponse(
        String userId,
        String username,
        String displayName,
        String mobile,
        String email,
        Integer status,
        Boolean superAdmin,
        Instant createTime) {
    public static SysUserResponse from(SysUserEntity entity) {
        return new SysUserResponse(
                String.valueOf(entity.getId()),
                entity.getUsername(),
                entity.getDisplayName(),
                entity.getMobile(),
                entity.getEmail(),
                entity.getStatus(),
                entity.getSuperAdmin(),
                entity.getCreateTime());
    }
}
