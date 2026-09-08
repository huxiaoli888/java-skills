package com.chaken.ai.test.cms.testtask.controller;

import com.chaken.ai.test.cms.testtask.dto.request.TestTaskPageQuery;
import com.chaken.ai.test.cms.testtask.dto.response.TestTaskDetailResponse;
import com.chaken.ai.test.cms.testtask.dto.response.TestTaskResponse;
import com.chaken.ai.test.common.api.ApiResult;
import com.chaken.ai.test.common.api.PageResult;
import com.chaken.ai.test.common.code.ErrorCode;
import com.chaken.ai.test.common.result.ServiceResult;
import com.chaken.ai.test.common.trace.TraceContext;
import com.chaken.ai.test.cms.testtask.model.TestTaskSummary;
import com.chaken.ai.test.cms.testtask.query.TestTaskPageCriteria;
import com.chaken.ai.test.cms.testtask.service.TestTaskQueryService;
import jakarta.validation.Valid;
import java.util.function.Function;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@Validated
@RestController
@RequestMapping("/api/v1/cms/test-tasks")
public class CmsTestTaskController {
    private final TestTaskQueryService testTaskQueryService;

    public CmsTestTaskController(TestTaskQueryService testTaskQueryService) {
        this.testTaskQueryService = testTaskQueryService;
    }

    @GetMapping
    public ApiResult<PageResult<TestTaskResponse>> pageTasks(@Valid @ModelAttribute TestTaskPageQuery query) {
        PageResult<TestTaskSummary> page = testTaskQueryService.pageTasks(new TestTaskPageCriteria(
                query.getAppId(),
                query.getStatus(),
                query.getPage(),
                query.getPageSize()));
        PageResult<TestTaskResponse> response = PageResult.of(
                page.getList().stream().map(TestTaskResponse::from).toList(),
                page.getTotal(),
                page.getPage(),
                page.getPageSize());
        return ApiResult.success(response, TraceContext.requestId());
    }

    @GetMapping("/{taskNo}")
    public ResponseEntity<ApiResult<TestTaskDetailResponse>> getTaskDetail(@PathVariable("taskNo") String taskNo) {
        return toResponse(testTaskQueryService.getTaskDetail(taskNo), TestTaskDetailResponse::from);
    }

    private <T, R> ResponseEntity<ApiResult<R>> toResponse(ServiceResult<T> result, Function<T, R> mapper) {
        if (result.isSuccess()) {
            return ResponseEntity.ok(ApiResult.success(mapper.apply(result.data()), TraceContext.requestId()));
        }

        ErrorCode errorCode = result.errorCode();
        return ResponseEntity.ok(ApiResult.fail(
                errorCode.code(),
                errorCode.defaultMessage(),
                TraceContext.requestId()));
    }
}
