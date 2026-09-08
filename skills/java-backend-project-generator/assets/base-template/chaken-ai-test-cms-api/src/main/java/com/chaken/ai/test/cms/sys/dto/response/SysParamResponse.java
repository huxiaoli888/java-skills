package com.chaken.ai.test.cms.sys.dto.response;

import com.chaken.ai.test.cms.sys.entity.SysParamEntity;

public record SysParamResponse(
        String paramId,
        String paramKey,
        String paramValue,
        String paramName,
        Integer status,
        String remark) {
    public static SysParamResponse from(SysParamEntity entity) {
        return new SysParamResponse(
                String.valueOf(entity.getId()),
                entity.getParamKey(),
                entity.getParamValue(),
                entity.getParamName(),
                entity.getStatus(),
                entity.getRemark());
    }
}
