package com.chaken.ai.test.cms.sampleitem.dto.request;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.Size;

public class SampleItemPageQuery {
    @Size(max = 64, message = "{common.size.invalid}")
    private String keyword;

    private Boolean enabled;

    @Min(value = 1, message = "{page.min}")
    private int page = 1;

    @Min(value = 1, message = "{page-size.min}")
    @Max(value = 100, message = "{page-size.max}")
    private int pageSize = 20;

    public String getKeyword() {
        return keyword;
    }

    public void setKeyword(String keyword) {
        this.keyword = keyword;
    }

    public Boolean getEnabled() {
        return enabled;
    }

    public void setEnabled(Boolean enabled) {
        this.enabled = enabled;
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
