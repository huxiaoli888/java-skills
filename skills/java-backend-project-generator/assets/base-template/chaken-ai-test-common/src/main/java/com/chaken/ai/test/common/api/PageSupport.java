package com.chaken.ai.test.common.api;

import java.util.Collections;
import java.util.List;

public final class PageSupport {
    private PageSupport() {
    }

    public static PageBounds calculate(int page, int pageSize, long total) {
        int normalizedPage = Math.max(page, 1);
        int normalizedPageSize = Math.max(pageSize, 1);
        long normalizedTotal = Math.max(total, 0);
        long fromIndex = Math.min(((long) normalizedPage - 1) * normalizedPageSize, normalizedTotal);
        long toIndex = Math.min(fromIndex + normalizedPageSize, normalizedTotal);
        return new PageBounds(normalizedPage, normalizedPageSize, fromIndex, toIndex);
    }

    public static <T> PageResult<T> ofList(List<T> all, int page, int pageSize) {
        List<T> source = all == null ? Collections.emptyList() : all;
        PageBounds bounds = calculate(page, pageSize, source.size());
        return PageResult.of(
                source.subList(bounds.fromIndexAsInt(), bounds.toIndexAsInt()),
                source.size(),
                bounds.page(),
                bounds.pageSize());
    }

    public record PageBounds(
            int page,
            int pageSize,
            long fromIndex,
            long toIndex) {
        public int fromIndexAsInt() {
            return Math.toIntExact(fromIndex);
        }

        public int toIndexAsInt() {
            return Math.toIntExact(toIndex);
        }
    }
}
