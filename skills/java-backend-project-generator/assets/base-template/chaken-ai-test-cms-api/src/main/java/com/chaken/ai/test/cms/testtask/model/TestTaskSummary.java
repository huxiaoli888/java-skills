package com.chaken.ai.test.cms.testtask.model;

import java.time.Instant;

public record TestTaskSummary(
        String taskNo,
        String appId,
        String taskName,
        String modelCode,
        TestTaskStatus status,
        Instant createdTime) {
}
