package {{basePackage}}.cms.sampleitem.converter;

import {{basePackage}}.cms.sampleitem.dto.request.SampleItemCreateRequest;
import {{basePackage}}.cms.sampleitem.dto.request.SampleItemUpdateRequest;
import {{basePackage}}.cms.sampleitem.dto.response.SampleItemDetailResponse;
import {{basePackage}}.cms.sampleitem.dto.response.SampleItemResponse;
import {{basePackage}}.cms.sampleitem.entity.SampleItemEntity;
import java.util.List;
import org.springframework.stereotype.Component;

@Component
public class SampleItemConverter {
    public SampleItemEntity toEntity(SampleItemCreateRequest request) {
        SampleItemEntity entity = new SampleItemEntity();
        entity.setName(request.getName());
        entity.setRemark(request.getRemark());
        return entity;
    }

    public void updateEntity(SampleItemEntity entity, SampleItemUpdateRequest request) {
        entity.setName(request.getName());
        entity.setRemark(request.getRemark());
        entity.setVersion(request.getVersion());
    }

    public SampleItemResponse toResponse(SampleItemEntity entity) {
        SampleItemResponse response = new SampleItemResponse();
        fillBaseResponse(response, entity);
        return response;
    }

    public SampleItemDetailResponse toDetailResponse(SampleItemEntity entity) {
        SampleItemDetailResponse response = new SampleItemDetailResponse();
        fillBaseResponse(response, entity);
        return response;
    }

    public List<SampleItemResponse> toResponseList(List<SampleItemEntity> entities) {
        return entities.stream().map(this::toResponse).toList();
    }

    private void fillBaseResponse(SampleItemResponse response, SampleItemEntity entity) {
        response.setId(entity.getId());
        response.setName(entity.getName());
        response.setRemark(entity.getRemark());
        response.setVersion(entity.getVersion());
        response.setCreateTime(entity.getCreateTime());
        response.setModifyTime(entity.getModifyTime());
    }
}
