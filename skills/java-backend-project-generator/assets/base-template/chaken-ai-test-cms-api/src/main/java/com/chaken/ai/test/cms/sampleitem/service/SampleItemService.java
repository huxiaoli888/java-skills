package com.chaken.ai.test.cms.sampleitem.service;

import com.chaken.ai.test.cms.sampleitem.dto.request.SampleItemCreateRequest;
import com.chaken.ai.test.cms.sampleitem.dto.request.SampleItemPageQuery;
import com.chaken.ai.test.cms.sampleitem.dto.request.SampleItemUpdateRequest;
import com.chaken.ai.test.cms.sampleitem.dto.response.SampleItemDetailResponse;
import com.chaken.ai.test.cms.sampleitem.dto.response.SampleItemResponse;
import com.chaken.ai.test.common.api.PageResult;
import com.chaken.ai.test.common.result.ServiceResult;

public interface SampleItemService {
    PageResult<SampleItemResponse> pageItems(SampleItemPageQuery query);

    ServiceResult<SampleItemDetailResponse> getItem(String itemId);

    SampleItemDetailResponse createItem(SampleItemCreateRequest request);

    ServiceResult<SampleItemDetailResponse> updateItem(String itemId, SampleItemUpdateRequest request);

    ServiceResult<Void> deleteItem(String itemId);
}
