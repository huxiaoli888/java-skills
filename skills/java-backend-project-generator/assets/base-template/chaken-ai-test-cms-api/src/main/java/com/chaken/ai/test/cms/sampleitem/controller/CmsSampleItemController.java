package com.chaken.ai.test.cms.sampleitem.controller;

import com.chaken.ai.test.cms.sampleitem.dto.request.SampleItemCreateRequest;
import com.chaken.ai.test.cms.sampleitem.dto.request.SampleItemPageQuery;
import com.chaken.ai.test.cms.sampleitem.dto.request.SampleItemUpdateRequest;
import com.chaken.ai.test.cms.sampleitem.dto.response.SampleItemDetailResponse;
import com.chaken.ai.test.cms.sampleitem.dto.response.SampleItemResponse;
import com.chaken.ai.test.cms.sampleitem.service.SampleItemService;
import com.chaken.ai.test.common.api.ApiResult;
import com.chaken.ai.test.common.api.PageResult;
import com.chaken.ai.test.common.log.annotation.OperationAudit;
import com.chaken.ai.test.common.log.model.OperationType;
import com.chaken.ai.test.common.code.ErrorCode;
import com.chaken.ai.test.common.result.ServiceResult;
import com.chaken.ai.test.common.trace.TraceContext;
import jakarta.validation.Valid;
import java.util.function.Function;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@Validated
@RestController
@RequestMapping("/api/v1/cms/sample-items")
public class CmsSampleItemController {
    private final SampleItemService sampleItemService;

    public CmsSampleItemController(SampleItemService sampleItemService) {
        this.sampleItemService = sampleItemService;
    }

    @GetMapping
    public ApiResult<PageResult<SampleItemResponse>> pageItems(@Valid @ModelAttribute SampleItemPageQuery query) {
        return ApiResult.success(sampleItemService.pageItems(query), TraceContext.requestId());
    }

    @GetMapping("/{itemId}")
    public ResponseEntity<ApiResult<SampleItemDetailResponse>> getItem(@PathVariable("itemId") String itemId) {
        return toResponse(sampleItemService.getItem(itemId), Function.identity());
    }

    @OperationAudit(action = "create sample item", type = OperationType.CREATE)
    @PostMapping
    public ApiResult<SampleItemDetailResponse> createItem(@Valid @RequestBody SampleItemCreateRequest request) {
        return ApiResult.success(sampleItemService.createItem(request), TraceContext.requestId());
    }

    @OperationAudit(action = "update sample item", type = OperationType.UPDATE)
    @PutMapping("/{itemId}")
    public ResponseEntity<ApiResult<SampleItemDetailResponse>> updateItem(
            @PathVariable("itemId") String itemId,
            @Valid @RequestBody SampleItemUpdateRequest request) {
        return toResponse(sampleItemService.updateItem(itemId, request), Function.identity());
    }

    @OperationAudit(action = "delete sample item", type = OperationType.DELETE)
    @DeleteMapping("/{itemId}")
    public ResponseEntity<ApiResult<Void>> deleteItem(@PathVariable("itemId") String itemId) {
        return toResponse(sampleItemService.deleteItem(itemId), ignored -> null);
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
