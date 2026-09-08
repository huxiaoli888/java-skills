package com.chaken.ai.test.cms.sys.dto.response;

import com.chaken.ai.test.cms.sys.entity.SysDictEntity;

public record SysDictResponse(
        String dictId,
        String dictCode,
        String dictName,
        Integer status,
        String remark) {
    public static SysDictResponse from(SysDictEntity entity) {
        return new SysDictResponse(
                String.valueOf(entity.getId()),
                entity.getDictCode(),
                entity.getDictName(),
                entity.getStatus(),
                entity.getRemark());
    }
}
