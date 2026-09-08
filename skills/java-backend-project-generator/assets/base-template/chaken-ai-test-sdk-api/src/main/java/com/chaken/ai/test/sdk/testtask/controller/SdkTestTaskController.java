package com.chaken.ai.test.sdk.testtask.controller;

import com.chaken.ai.test.common.api.ApiResult;
import com.chaken.ai.test.common.code.ErrorCode;
import com.chaken.ai.test.common.result.ServiceResult;
import com.chaken.ai.test.common.trace.TraceContext;
import com.chaken.ai.test.sdk.testtask.dto.request.CreateTestTaskRequest;
import com.chaken.ai.test.sdk.testtask.dto.response.CreateTestTaskResponse;
import com.chaken.ai.test.sdk.testtask.dto.response.TestTaskStatusResponse;
import com.chaken.ai.test.sdk.testtask.service.TestTaskService;
import com.chaken.ai.test.security.signature.SignatureHeaders;
import com.chaken.ai.test.sdk.security.SdkSecurityFilter;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/sdk/test-tasks")
public class SdkTestTaskController {
    private final TestTaskService testTaskService;

    public SdkTestTaskController(TestTaskService testTaskService) {
        this.testTaskService = testTaskService;
    }

    @PostMapping
    public ResponseEntity<ApiResult<CreateTestTaskResponse>> createTask(
            @RequestHeader(SignatureHeaders.API_KEY) String apiKey,
            @RequestHeader(SignatureHeaders.TIMESTAMP) String timestamp,
            @RequestHeader(SignatureHeaders.REQID) String reqid,
            @RequestHeader(SignatureHeaders.SIGNATURE_ALG) String signatureAlg,
            @RequestHeader(SignatureHeaders.API_VERSION) String apiVersion,
            @RequestHeader(SignatureHeaders.SIGN) String sign,
            @Valid @RequestBody CreateTestTaskRequest request,
            HttpServletRequest servletRequest) {
        return toResponse(testTaskService.createTask(
                apiKey,
                request,
                requestFingerprint(servletRequest)));
    }

    @GetMapping("/{taskNo}")
    public ResponseEntity<ApiResult<TestTaskStatusResponse>> getTaskStatus(
            @RequestHeader(SignatureHeaders.API_KEY) String apiKey,
            @RequestHeader(SignatureHeaders.SIGN) String sign,
            @PathVariable("taskNo") String taskNo) {
        return toResponse(testTaskService.getTaskStatus(taskNo));
    }

    private String requestFingerprint(HttpServletRequest request) {
        Object value = request.getAttribute(SdkSecurityFilter.REQUEST_FINGERPRINT_ATTRIBUTE);
        return value == null ? "" : String.valueOf(value);
    }

    private <T> ResponseEntity<ApiResult<T>> toResponse(ServiceResult<T> result) {
        if (result.isSuccess()) {
            return ResponseEntity.ok(ApiResult.success(result.data(), TraceContext.requestId()));
        }
        ErrorCode errorCode = result.errorCode();
        return ResponseEntity.ok(ApiResult.fail(
                errorCode.code(),
                errorCode.defaultMessage(),
                TraceContext.requestId()));
    }
}
