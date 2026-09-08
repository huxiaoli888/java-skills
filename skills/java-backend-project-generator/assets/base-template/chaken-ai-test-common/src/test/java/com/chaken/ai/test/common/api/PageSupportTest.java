package com.chaken.ai.test.common.api;

import org.junit.jupiter.api.Test;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

class PageSupportTest {
    @Test
    void calculateNormalizesInvalidPageArguments() {
        PageSupport.PageBounds bounds = PageSupport.calculate(0, 0, 3);

        assertThat(bounds.page()).isEqualTo(1);
        assertThat(bounds.pageSize()).isEqualTo(1);
        assertThat(bounds.fromIndex()).isZero();
        assertThat(bounds.toIndex()).isEqualTo(1);
    }

    @Test
    void calculateCapsIndexesAtTotalSize() {
        PageSupport.PageBounds bounds = PageSupport.calculate(3, 2, 5);

        assertThat(bounds.fromIndex()).isEqualTo(4);
        assertThat(bounds.toIndex()).isEqualTo(5);
    }

    @Test
    void ofListReturnsCurrentPageResult() {
        PageResult<String> page = PageSupport.ofList(List.of("a", "b", "c"), 2, 2);

        assertThat(page.getList()).containsExactly("c");
        assertThat(page.getTotal()).isEqualTo(3);
        assertThat(page.getPage()).isEqualTo(2);
        assertThat(page.getPageSize()).isEqualTo(2);
        assertThat(page.getPages()).isEqualTo(2);
    }
}
