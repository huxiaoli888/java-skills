package {{basePackage}}.cms.sampleitem.service.impl;

import {{basePackage}}.cms.sampleitem.converter.SampleItemConverter;
import {{basePackage}}.cms.sampleitem.dto.request.SampleItemCreateRequest;
import {{basePackage}}.cms.sampleitem.dto.request.SampleItemPageQuery;
import {{basePackage}}.cms.sampleitem.dto.request.SampleItemUpdateRequest;
import {{basePackage}}.cms.sampleitem.dto.response.SampleItemDetailResponse;
import {{basePackage}}.cms.sampleitem.dto.response.SampleItemResponse;
import {{basePackage}}.cms.sampleitem.entity.SampleItemEntity;
import {{basePackage}}.cms.sampleitem.mapper.SampleItemMapper;
import {{basePackage}}.cms.sampleitem.service.SampleItemService;
import {{basePackage}}.common.api.PageResult;
import {{basePackage}}.common.code.CommonErrorCode;
import {{basePackage}}.common.persistence.EntityAuditFillSupport;
import {{basePackage}}.common.persistence.LogicDeleteFlag;
import {{basePackage}}.common.result.ServiceResult;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import java.util.Map;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

@Service
public class SampleItemServiceImpl implements SampleItemService {
    private static final Map<String, String> SORT_COLUMNS = Map.of(
            "createTime", "create_time",
            "modifyTime", "modify_time",
            "name", "name");

    private final SampleItemMapper mapper;
    private final SampleItemConverter converter;
    private final EntityAuditFillSupport auditFillSupport;

    public SampleItemServiceImpl(
            SampleItemMapper mapper,
            SampleItemConverter converter,
            EntityAuditFillSupport auditFillSupport) {
        this.mapper = mapper;
        this.converter = converter;
        this.auditFillSupport = auditFillSupport;
    }

    @Override
    @Transactional
    public ServiceResult<SampleItemDetailResponse> create(SampleItemCreateRequest request) {
        if (!isNameUnique(request.getName(), null)) {
            return ServiceResult.failure(CommonErrorCode.DUPLICATE_RESOURCE);
        }
        SampleItemEntity entity = converter.toEntity(request);
        auditFillSupport.fillForInsert(entity);
        mapper.insert(entity);
        return ServiceResult.success(converter.toDetailResponse(entity));
    }

    @Override
    @Transactional
    public ServiceResult<SampleItemDetailResponse> update(Long id, SampleItemUpdateRequest request) {
        ServiceResult<SampleItemEntity> currentResult = getNormalEntity(id);
        if (!currentResult.isSuccess()) {
            return ServiceResult.failure(currentResult.errorCode());
        }
        SampleItemEntity current = currentResult.data();
        if (!current.getVersion().equals(request.getVersion())) {
            return ServiceResult.failure(CommonErrorCode.CONCURRENT_MODIFICATION);
        }
        if (!isNameUnique(request.getName(), id)) {
            return ServiceResult.failure(CommonErrorCode.DUPLICATE_RESOURCE);
        }
        converter.updateEntity(current, request);
        auditFillSupport.fillForUpdate(current);
        int updated = mapper.updateById(current);
        if (updated != 1) {
            return ServiceResult.failure(CommonErrorCode.CONCURRENT_MODIFICATION);
        }
        return ServiceResult.success(converter.toDetailResponse(current));
    }

    @Override
    @Transactional
    public ServiceResult<Void> delete(Long id) {
        ServiceResult<SampleItemEntity> currentResult = getNormalEntity(id);
        if (!currentResult.isSuccess()) {
            return ServiceResult.failure(currentResult.errorCode());
        }
        SampleItemEntity current = currentResult.data();
        auditFillSupport.fillForLogicDelete(current);
        int updated = mapper.update(null, new LambdaUpdateWrapper<SampleItemEntity>()
                .eq(SampleItemEntity::getId, id)
                .eq(SampleItemEntity::getDeleted, LogicDeleteFlag.NORMAL)
                .set(SampleItemEntity::getDeleted, LogicDeleteFlag.DELETED)
                .set(SampleItemEntity::getModifyBy, current.getModifyBy())
                .set(SampleItemEntity::getModifyTime, current.getModifyTime()));
        if (updated != 1) {
            return ServiceResult.failure(CommonErrorCode.CONCURRENT_MODIFICATION);
        }
        return ServiceResult.success(null);
    }

    @Override
    public PageResult<SampleItemResponse> page(SampleItemPageQuery query) {
        LambdaQueryWrapper<SampleItemEntity> wrapper = normalWrapper();
        if (StringUtils.hasText(query.getName())) {
            wrapper.like(SampleItemEntity::getName, query.getName());
        }
        applySort(wrapper, query.getSort());
        Page<SampleItemEntity> page = mapper.selectPage(Page.of(query.getPage(), query.getPageSize()), wrapper);
        return PageResult.of(
                converter.toResponseList(page.getRecords()),
                page.getTotal(),
                query.getPage(),
                query.getPageSize());
    }

    @Override
    public ServiceResult<SampleItemDetailResponse> detail(Long id) {
        ServiceResult<SampleItemEntity> result = getNormalEntity(id);
        if (!result.isSuccess()) {
            return ServiceResult.failure(result.errorCode());
        }
        return ServiceResult.success(converter.toDetailResponse(result.data()));
    }

    private ServiceResult<SampleItemEntity> getNormalEntity(Long id) {
        SampleItemEntity entity = mapper.selectOne(normalWrapper().eq(SampleItemEntity::getId, id));
        if (entity == null) {
            return ServiceResult.failure(CommonErrorCode.RESOURCE_NOT_FOUND);
        }
        return ServiceResult.success(entity);
    }

    private boolean isNameUnique(String name, Long excludeId) {
        LambdaQueryWrapper<SampleItemEntity> wrapper = normalWrapper().eq(SampleItemEntity::getName, name);
        if (excludeId != null) {
            wrapper.ne(SampleItemEntity::getId, excludeId);
        }
        return mapper.selectCount(wrapper) == 0;
    }

    private LambdaQueryWrapper<SampleItemEntity> normalWrapper() {
        return new LambdaQueryWrapper<SampleItemEntity>()
                .eq(SampleItemEntity::getDeleted, LogicDeleteFlag.NORMAL);
    }

    private void applySort(LambdaQueryWrapper<SampleItemEntity> wrapper, String sort) {
        if (!StringUtils.hasText(sort)) {
            wrapper.orderByDesc(SampleItemEntity::getCreateTime);
            return;
        }
        String column = SORT_COLUMNS.get(sort);
        if (column == null) {
            wrapper.orderByDesc(SampleItemEntity::getCreateTime);
            return;
        }
        wrapper.last("order by " + column + " desc");
    }
}
