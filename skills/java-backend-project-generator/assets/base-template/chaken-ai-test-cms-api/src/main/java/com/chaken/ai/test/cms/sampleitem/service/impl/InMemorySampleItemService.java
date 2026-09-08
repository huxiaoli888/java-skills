package com.chaken.ai.test.cms.sampleitem.service.impl;

import com.chaken.ai.test.cms.sampleitem.dto.request.SampleItemCreateRequest;
import com.chaken.ai.test.cms.sampleitem.dto.request.SampleItemPageQuery;
import com.chaken.ai.test.cms.sampleitem.dto.request.SampleItemUpdateRequest;
import com.chaken.ai.test.cms.sampleitem.dto.response.SampleItemDetailResponse;
import com.chaken.ai.test.cms.sampleitem.dto.response.SampleItemResponse;
import com.chaken.ai.test.cms.sampleitem.service.SampleItemService;
import com.chaken.ai.test.common.api.PageResult;
import com.chaken.ai.test.common.api.PageSupport;
import com.chaken.ai.test.common.code.CommonErrorCode;
import com.chaken.ai.test.common.result.ServiceResult;
import java.time.Instant;
import java.util.Comparator;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.atomic.AtomicLong;
import org.springframework.stereotype.Service;

@Service
public class InMemorySampleItemService implements SampleItemService {
    private final AtomicLong sequence = new AtomicLong(1000);
    private final ConcurrentMap<String, SampleItemDetailResponse> items = new ConcurrentHashMap<>();

    @Override
    public SampleItemDetailResponse createItem(SampleItemCreateRequest request) {
        String itemId = "ITEM" + sequence.incrementAndGet();
        Instant now = Instant.now();
        SampleItemDetailResponse detail = new SampleItemDetailResponse(
                itemId,
                request.getName(),
                request.getCode(),
                value(request.getDescription()),
                enabled(request.getEnabled()),
                now.toEpochMilli(),
                now.toEpochMilli());
        items.put(itemId, detail);
        return detail;
    }

    @Override
    public ServiceResult<SampleItemDetailResponse> updateItem(String itemId, SampleItemUpdateRequest request) {
        ServiceResult<SampleItemDetailResponse> current = getItem(itemId);
        if (!current.isSuccess()) {
            return current;
        }
        SampleItemDetailResponse existing = current.data();
        SampleItemDetailResponse updated = new SampleItemDetailResponse(
                existing.itemId(),
                request.getName(),
                request.getCode(),
                value(request.getDescription()),
                enabled(request.getEnabled()),
                existing.createdTime(),
                Instant.now().toEpochMilli());
        items.put(updated.itemId(), updated);
        return ServiceResult.success(updated);
    }

    @Override
    public ServiceResult<Void> deleteItem(String itemId) {
        if (items.remove(itemId) == null) {
            return ServiceResult.failure(CommonErrorCode.RESOURCE_NOT_FOUND);
        }
        return ServiceResult.success(null);
    }

    @Override
    public PageResult<SampleItemResponse> pageItems(SampleItemPageQuery query) {
        String keyword = value(query.getKeyword()).toLowerCase();
        List<SampleItemResponse> all = items.values()
                .stream()
                .filter(item -> query.getEnabled() == null || query.getEnabled() == item.enabled())
                .filter(item -> keyword.isEmpty()
                        || item.name().toLowerCase().contains(keyword)
                        || item.code().toLowerCase().contains(keyword))
                .sorted(Comparator.comparing(SampleItemDetailResponse::updatedTime).reversed())
                .map(item -> new SampleItemResponse(
                        item.itemId(),
                        item.name(),
                        item.code(),
                        item.enabled(),
                        item.updatedTime()))
                .toList();
        return PageSupport.ofList(all, query.getPage(), query.getPageSize());
    }

    @Override
    public ServiceResult<SampleItemDetailResponse> getItem(String itemId) {
        SampleItemDetailResponse detail = items.get(itemId);
        if (detail == null) {
            return ServiceResult.failure(CommonErrorCode.RESOURCE_NOT_FOUND);
        }
        return ServiceResult.success(detail);
    }

    private boolean enabled(Boolean enabled) {
        return enabled == null || enabled;
    }

    private String value(String value) {
        return value == null ? "" : value.trim();
    }
}
