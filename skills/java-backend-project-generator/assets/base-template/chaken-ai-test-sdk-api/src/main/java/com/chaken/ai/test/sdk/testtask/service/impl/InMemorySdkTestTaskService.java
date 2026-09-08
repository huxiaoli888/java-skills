package com.chaken.ai.test.sdk.testtask.service.impl;

import com.chaken.ai.test.common.code.CommonErrorCode;
import com.chaken.ai.test.common.result.ServiceResult;
import com.chaken.ai.test.sdk.idempotency.InMemoryBusinessIdempotencyService;
import com.chaken.ai.test.sdk.testtask.dto.request.CreateTestTaskRequest;
import com.chaken.ai.test.sdk.testtask.dto.response.CreateTestTaskResponse;
import com.chaken.ai.test.sdk.testtask.dto.response.TestTaskStatusResponse;
import com.chaken.ai.test.sdk.testtask.service.TestTaskService;
import com.chaken.ai.test.security.idempotency.IdempotencyDecision;
import java.time.Instant;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import org.springframework.stereotype.Service;

@Service
public class InMemorySdkTestTaskService implements TestTaskService {
    private static final String BUSINESS_TYPE_CREATE = "TEST_TASK_CREATE";

    private final ConcurrentMap<String, TestTaskDetail> tasks = new ConcurrentHashMap<>();
    private final ConcurrentMap<String, String> taskNoByBusinessKey = new ConcurrentHashMap<>();
    private final InMemoryBusinessIdempotencyService idempotencyService;

    public InMemorySdkTestTaskService(InMemoryBusinessIdempotencyService idempotencyService) {
        this.idempotencyService = idempotencyService;
    }

    @Override
    public ServiceResult<CreateTestTaskResponse> createTask(String apiKey, CreateTestTaskRequest request, String requestFingerprint) {
        String businessKey = firstNonBlank(request.getBusinessNo(), request.getRequestNo());
        IdempotencyDecision decision = idempotencyService.check(
                apiKey,
                requestFingerprint,
                BUSINESS_TYPE_CREATE,
                businessKey);
        if (decision == IdempotencyDecision.CONFLICT_DIFFERENT_REQUEST) {
            return ServiceResult.failure(CommonErrorCode.IDEMPOTENCY_CONFLICT);
        }
        if (decision == IdempotencyDecision.REPLAY_SAME_REQUEST) {
            return replayCreated(apiKey, businessKey);
        }

        String taskNo = "TASK" + System.currentTimeMillis();
        Instant now = Instant.now();
        TestTaskDetail detail = new TestTaskDetail(
                taskNo,
                apiKey,
                request.getRequestNo(),
                request.getBusinessNo(),
                request.getTaskName(),
                request.getModelCode(),
                TestTaskStatus.CREATED,
                "created",
                now,
                now);
        tasks.put(taskNo, detail);
        taskNoByBusinessKey.put(apiKey + ":" + businessKey, taskNo);
        idempotencyService.saveResult(apiKey, BUSINESS_TYPE_CREATE, businessKey, taskNo);
        return ServiceResult.success(new CreateTestTaskResponse(taskNo, request.getRequestNo(), detail.status().name()));
    }

    @Override
    public ServiceResult<TestTaskStatusResponse> getTaskStatus(String taskNo) {
        ServiceResult<TestTaskDetail> result = getTaskDetail(taskNo);
        if (!result.isSuccess()) {
            return ServiceResult.failure(result.errorCode());
        }
        TestTaskDetail detail = result.data();
        return ServiceResult.success(new TestTaskStatusResponse(
                detail.taskNo(),
                detail.status().name(),
                detail.statusMessage(),
                detail.updatedTime().toEpochMilli()));
    }

    private ServiceResult<TestTaskDetail> getTaskDetail(String taskNo) {
        TestTaskDetail detail = tasks.get(taskNo);
        if (detail == null) {
            return ServiceResult.failure(CommonErrorCode.RESOURCE_NOT_FOUND);
        }
        return ServiceResult.success(detail);
    }

    private boolean isBlank(String value) {
        return value == null || value.trim().isEmpty();
    }

    private String firstNonBlank(String primary, String fallback) {
        return isBlank(primary) ? fallback : primary;
    }

    private ServiceResult<CreateTestTaskResponse> replayCreated(String apiKey, String businessKey) {
        String taskNo = taskNoByBusinessKey.get(apiKey + ":" + businessKey);
        if (taskNo == null) {
            taskNo = idempotencyService.resultSnapshot(apiKey, BUSINESS_TYPE_CREATE, businessKey);
        }
        ServiceResult<TestTaskDetail> result = getTaskDetail(taskNo);
        if (!result.isSuccess()) {
            return ServiceResult.failure(result.errorCode());
        }
        TestTaskDetail detail = result.data();
        return ServiceResult.success(new CreateTestTaskResponse(detail.taskNo(), detail.requestNo(), detail.status().name()));
    }

    private enum TestTaskStatus {
        CREATED,
        RUNNING,
        SUCCEEDED,
        FAILED,
        CANCELED
    }

    private record TestTaskDetail(
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
}
