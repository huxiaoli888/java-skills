package com.chaken.ai.test.cms.testtask.service;

import com.chaken.ai.test.cms.testtask.model.TestTaskDetail;
import com.chaken.ai.test.cms.testtask.model.TestTaskSummary;
import com.chaken.ai.test.cms.testtask.query.TestTaskPageCriteria;
import com.chaken.ai.test.common.api.PageResult;
import com.chaken.ai.test.common.result.ServiceResult;

public interface TestTaskQueryService {
    PageResult<TestTaskSummary> pageTasks(TestTaskPageCriteria criteria);

    ServiceResult<TestTaskDetail> getTaskDetail(String taskNo);
}
