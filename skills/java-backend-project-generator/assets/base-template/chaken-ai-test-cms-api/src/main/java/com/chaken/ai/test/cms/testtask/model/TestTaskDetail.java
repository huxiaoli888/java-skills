package com.chaken.ai.test.cms.testtask.model;

import java.time.Instant;

public record TestTaskDetail(
        String taskNo,
        String appId,
        String requestNo,
        String businessNo,
        String taskName,
        String modelCode,
        TestTaskStatus status,
        String statusMessage,
        Instant createdTime,
        Instant updatedTime) {
}
