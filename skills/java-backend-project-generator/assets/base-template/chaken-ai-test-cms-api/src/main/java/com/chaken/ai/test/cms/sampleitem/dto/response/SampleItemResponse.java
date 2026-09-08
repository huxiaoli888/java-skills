package com.chaken.ai.test.cms.sampleitem.dto.response;

public record SampleItemResponse(
        String itemId,
        String name,
        String code,
        boolean enabled,
        long updatedTime) {
}
