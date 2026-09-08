package com.chaken.ai.test.sdk.testtask.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class CreateTestTaskRequest {
    @NotBlank(message = "{test-task.request-no.required}")
    @Size(max = 64, message = "{test-task.request-no.size}")
    private String requestNo;

    @Size(max = 64, message = "{test-task.business-no.size}")
    private String businessNo;

    @NotBlank(message = "{test-task.task-name.required}")
    @Size(max = 128, message = "{test-task.task-name.size}")
    private String taskName;

    @NotBlank(message = "{test-task.model-code.required}")
    @Size(max = 64, message = "{test-task.model-code.size}")
    private String modelCode;

    @Size(max = 512, message = "{test-task.callback-url.size}")
    private String callbackUrl;

    public String getRequestNo() {
        return requestNo;
    }

    public void setRequestNo(String requestNo) {
        this.requestNo = requestNo;
    }

    public String getBusinessNo() {
        return businessNo;
    }

    public void setBusinessNo(String businessNo) {
        this.businessNo = businessNo;
    }

    public String getTaskName() {
        return taskName;
    }

    public void setTaskName(String taskName) {
        this.taskName = taskName;
    }

    public String getModelCode() {
        return modelCode;
    }

    public void setModelCode(String modelCode) {
        this.modelCode = modelCode;
    }

    public String getCallbackUrl() {
        return callbackUrl;
    }

    public void setCallbackUrl(String callbackUrl) {
        this.callbackUrl = callbackUrl;
    }
}
