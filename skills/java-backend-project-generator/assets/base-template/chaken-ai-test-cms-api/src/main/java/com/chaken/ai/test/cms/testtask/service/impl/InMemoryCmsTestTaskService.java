package com.chaken.ai.test.cms.testtask.service.impl;

import com.chaken.ai.test.cms.testtask.model.TestTaskDetail;
import com.chaken.ai.test.cms.testtask.model.TestTaskSummary;
import com.chaken.ai.test.cms.testtask.query.TestTaskPageCriteria;
import com.chaken.ai.test.cms.testtask.service.TestTaskQueryService;
import com.chaken.ai.test.common.api.PageResult;
import com.chaken.ai.test.common.api.PageSupport;
import com.chaken.ai.test.common.code.CommonErrorCode;
import com.chaken.ai.test.common.result.ServiceResult;
import java.util.Comparator;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import org.springframework.stereotype.Service;

@Service
public class InMemoryCmsTestTaskService implements TestTaskQueryService {
    private final ConcurrentMap<String, TestTaskDetail> tasks = new ConcurrentHashMap<>();

    @Override
    public PageResult<TestTaskSummary> pageTasks(TestTaskPageCriteria criteria) {
        List<TestTaskSummary> all = tasks.values()
                .stream()
                .filter(task -> isBlank(criteria.appId()) || criteria.appId().equals(task.appId()))
                .filter(task -> isBlank(criteria.status()) || criteria.status().equals(task.status().name()))
                .sorted(Comparator.comparing(TestTaskDetail::createdTime).reversed())
                .map(task -> new TestTaskSummary(
                        task.taskNo(),
                        task.appId(),
                        task.taskName(),
                        task.modelCode(),
                        task.status(),
                        task.createdTime()))
                .toList();
        return PageSupport.ofList(all, criteria.page(), criteria.pageSize());
    }

    @Override
    public ServiceResult<TestTaskDetail> getTaskDetail(String taskNo) {
        TestTaskDetail detail = tasks.get(taskNo);
        if (detail == null) {
            return ServiceResult.failure(CommonErrorCode.RESOURCE_NOT_FOUND);
        }
        return ServiceResult.success(detail);
    }

    private boolean isBlank(String value) {
        return value == null || value.trim().isEmpty();
    }
}
