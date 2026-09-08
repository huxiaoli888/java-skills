package com.chaken.ai.test.cms.testtask.dto.response;

import com.chaken.ai.test.cms.testtask.model.TestTaskDetail;

public record TestTaskDetailResponse(
        String taskNo,
        String appId,
        String requestNo,
        String businessNo,
        String taskName,
        String modelCode,
        String status,
        String statusMessage,
        long createdTime,
        long updatedTime) {
    public static TestTaskDetailResponse from(TestTaskDetail detail) {
        return new TestTaskDetailResponse(
                detail.taskNo(),
                detail.appId(),
                detail.requestNo(),
                detail.businessNo(),
                detail.taskName(),
                detail.modelCode(),
                detail.status().name(),
                detail.statusMessage(),
                detail.createdTime().toEpochMilli(),
                detail.updatedTime().toEpochMilli());
    }
}
