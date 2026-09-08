package com.chaken.ai.test.cms.testtask.query;

public record TestTaskPageCriteria(
        String appId,
        String status,
        int page,
        int pageSize) {
}
