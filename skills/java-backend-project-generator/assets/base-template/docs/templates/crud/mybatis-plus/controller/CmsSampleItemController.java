package {{basePackage}}.cms.sampleitem.controller;

import {{basePackage}}.cms.sampleitem.dto.request.SampleItemCreateRequest;
import {{basePackage}}.cms.sampleitem.dto.request.SampleItemPageQuery;
import {{basePackage}}.cms.sampleitem.dto.request.SampleItemUpdateRequest;
import {{basePackage}}.cms.sampleitem.dto.response.SampleItemDetailResponse;
import {{basePackage}}.cms.sampleitem.dto.response.SampleItemResponse;
import {{basePackage}}.cms.sampleitem.service.SampleItemService;
import {{basePackage}}.common.api.ApiResult;
import {{basePackage}}.common.api.PageResult;
import {{basePackage}}.common.log.annotation.OperationAudit;
import {{basePackage}}.common.log.model.OperationType;
import {{basePackage}}.common.code.ErrorCode;
import {{basePackage}}.common.result.ServiceResult;
import {{basePackage}}.common.trace.TraceContext;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotNull;
import java.util.function.Function;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
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
    public ApiResult<PageResult<SampleItemResponse>> page(@Valid SampleItemPageQuery query) {
        return ApiResult.success(sampleItemService.page(query), TraceContext.requestId());
    }

    @PostMapping
    @OperationAudit(type = OperationType.CREATE, action = "sample-item-create")
    public ResponseEntity<ApiResult<SampleItemDetailResponse>> create(@Valid @RequestBody SampleItemCreateRequest request) {
        return toResponse(sampleItemService.create(request), Function.identity());
    }

    @GetMapping("/{id}")
    public ResponseEntity<ApiResult<SampleItemDetailResponse>> detail(@NotNull(message = "{sampleItem.id.required}") @PathVariable Long id) {
        return toResponse(sampleItemService.detail(id), Function.identity());
    }

    @PutMapping("/{id}")
    @OperationAudit(type = OperationType.UPDATE, action = "sample-item-update")
    public ResponseEntity<ApiResult<SampleItemDetailResponse>> update(
            @NotNull(message = "{sampleItem.id.required}") @PathVariable Long id,
            @Valid @RequestBody SampleItemUpdateRequest request) {
        return toResponse(sampleItemService.update(id, request), Function.identity());
    }

    @DeleteMapping("/{id}")
    @OperationAudit(type = OperationType.DELETE, action = "sample-item-delete")
    public ResponseEntity<ApiResult<Void>> delete(@NotNull(message = "{sampleItem.id.required}") @PathVariable Long id) {
        return toResponse(sampleItemService.delete(id), ignored -> null);
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
