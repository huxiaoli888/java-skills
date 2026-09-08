package com.chaken.ai.test.cms.sampleitem.dto.response;

public record SampleItemDetailResponse(
        String itemId,
        String name,
        String code,
        String description,
        boolean enabled,
        long createdTime,
        long updatedTime) {
}
