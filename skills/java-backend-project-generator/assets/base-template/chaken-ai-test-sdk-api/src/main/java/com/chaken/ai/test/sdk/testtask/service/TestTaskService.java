package com.chaken.ai.test.sdk.testtask.service;

import com.chaken.ai.test.common.result.ServiceResult;
import com.chaken.ai.test.sdk.testtask.dto.request.CreateTestTaskRequest;
import com.chaken.ai.test.sdk.testtask.dto.response.CreateTestTaskResponse;
import com.chaken.ai.test.sdk.testtask.dto.response.TestTaskStatusResponse;

public interface TestTaskService {
    ServiceResult<CreateTestTaskResponse> createTask(String apiKey, CreateTestTaskRequest request, String requestFingerprint);

    ServiceResult<TestTaskStatusResponse> getTaskStatus(String taskNo);
}
