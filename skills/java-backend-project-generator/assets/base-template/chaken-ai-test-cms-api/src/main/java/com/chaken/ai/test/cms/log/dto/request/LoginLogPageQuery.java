package com.chaken.ai.test.cms.log.dto.request;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;

public class LoginLogPageQuery {
    private String keyword;
    private Integer status;
    @Min(1)
    private int page = 1;
    @Min(1)
    @Max(200)
    private int pageSize = 20;

    public String getKeyword() {
        return keyword;
    }

    public void setKeyword(String keyword) {
        this.keyword = keyword;
    }

    public Integer getStatus() {
        return status;
    }

    public void setStatus(Integer status) {
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
