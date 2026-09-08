package com.chaken.ai.test.sdk.testtask.dto.response;

public record TestTaskStatusResponse(
        String taskNo,
        String status,
        String statusMessage,
        long updatedTime) {
}
