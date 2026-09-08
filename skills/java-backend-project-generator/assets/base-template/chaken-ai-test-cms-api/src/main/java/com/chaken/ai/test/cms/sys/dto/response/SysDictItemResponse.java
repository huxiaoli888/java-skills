package com.chaken.ai.test.cms.sys.dto.response;

import com.chaken.ai.test.cms.sys.entity.SysDictItemEntity;

public record SysDictItemResponse(
        String itemId,
        String dictCode,
        String itemValue,
        String itemLabel,
        Integer sortNo,
        Integer status,
        String remark) {
    public static SysDictItemResponse from(SysDictItemEntity entity) {
        return new SysDictItemResponse(
                String.valueOf(entity.getId()),
                entity.getDictCode(),
                entity.getItemValue(),
                entity.getItemLabel(),
                entity.getSortNo(),
                entity.getStatus(),
                entity.getRemark());
    }
}
