package com.chaken.ai.test.cms.testtask.dto.response;

import com.chaken.ai.test.cms.testtask.model.TestTaskSummary;

public record TestTaskResponse(
        String taskNo,
        String appId,
        String taskName,
        String modelCode,
        String status,
        long createdTime) {
    public static TestTaskResponse from(TestTaskSummary summary) {
        return new TestTaskResponse(
                summary.taskNo(),
                summary.appId(),
                summary.taskName(),
                summary.modelCode(),
                summary.status().name(),
                summary.createdTime().toEpochMilli());
    }
}
