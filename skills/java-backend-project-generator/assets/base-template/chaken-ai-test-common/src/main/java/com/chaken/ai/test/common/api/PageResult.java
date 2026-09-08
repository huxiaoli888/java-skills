package com.chaken.ai.test.common.api;

import java.util.Collections;
import java.util.List;

public class PageResult<T> {
    private List<T> list;
    private long total;
    private int page;
    private int pageSize;
    private long pages;

    public PageResult() {
    }

    public PageResult(List<T> list, long total, int page, int pageSize) {
        this.list = list == null ? Collections.emptyList() : list;
        this.total = total;
        this.page = page;
        this.pageSize = pageSize;
        this.pages = pageSize <= 0 ? 0 : (total + pageSize - 1) / pageSize;
    }

    public static <T> PageResult<T> of(List<T> list, long total, int page, int pageSize) {
        return new PageResult<>(list, total, page, pageSize);
    }

    public List<T> getList() {
        return list;
    }

    public void setList(List<T> list) {
        this.list = list;
    }

    public long getTotal() {
        return total;
    }

    public void setTotal(long total) {
        this.total = total;
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

    public long getPages() {
        return pages;
    }

    public void setPages(long pages) {
        this.pages = pages;
    }
}
