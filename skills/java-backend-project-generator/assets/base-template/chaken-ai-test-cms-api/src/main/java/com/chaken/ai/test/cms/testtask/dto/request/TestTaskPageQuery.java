package com.chaken.ai.test.cms.testtask.dto.request;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.Size;

public class TestTaskPageQuery {
    @Size(max = 64, message = "{test-task.app-id.size}")
    private String appId;

    @Size(max = 32, message = "{test-task.status.size}")
    private String status;

    @Min(value = 1, message = "{page.min}")
    private int page = 1;

    @Min(value = 1, message = "{page-size.min}")
    @Max(value = 100, message = "{page-size.max}")
    private int pageSize = 20;

    public String getAppId() {
        return appId;
    }

    public void setAppId(String appId) {
        this.appId = appId;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public int getPage() {
        return page;
    }

    public void setPage(int page) {
        this.page = page;
    }

    public int getPageSize() {
        return pageSize;
    }

    public void setPageSize(int pageSize) {
        this.pageSize = pageSize;
    }
}
