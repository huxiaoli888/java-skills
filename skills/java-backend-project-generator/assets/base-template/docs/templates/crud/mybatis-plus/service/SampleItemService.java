package {{basePackage}}.cms.sampleitem.service;

import {{basePackage}}.cms.sampleitem.dto.request.SampleItemCreateRequest;
import {{basePackage}}.cms.sampleitem.dto.request.SampleItemPageQuery;
import {{basePackage}}.cms.sampleitem.dto.request.SampleItemUpdateRequest;
import {{basePackage}}.cms.sampleitem.dto.response.SampleItemDetailResponse;
import {{basePackage}}.cms.sampleitem.dto.response.SampleItemResponse;
import {{basePackage}}.common.api.PageResult;
import {{basePackage}}.common.result.ServiceResult;

public interface SampleItemService {
    PageResult<SampleItemResponse> page(SampleItemPageQuery query);

    ServiceResult<SampleItemDetailResponse> detail(Long id);

    ServiceResult<SampleItemDetailResponse> create(SampleItemCreateRequest request);

    ServiceResult<SampleItemDetailResponse> update(Long id, SampleItemUpdateRequest request);

    ServiceResult<Void> delete(Long id);
}
