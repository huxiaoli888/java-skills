package com.chaken.ai.test.cms.log.service.impl;

import com.chaken.ai.test.cms.log.entity.OperationLogEntity;
import com.chaken.ai.test.cms.log.mapper.OperationLogMapper;
import com.chaken.ai.test.common.log.model.OperationAuditRecord;
import com.chaken.ai.test.common.log.service.OperationAuditService;
import java.time.Instant;
import org.springframework.context.annotation.Primary;
import org.springframework.stereotype.Service;

@Service
@Primary
public class DbOperationAuditService implements OperationAuditService {
    private final OperationLogMapper mapper;

    public DbOperationAuditService(OperationLogMapper mapper) {
        this.mapper = mapper;
    }

    @Override
    public void save(OperationAuditRecord record) {
        OperationLogEntity entity = new OperationLogEntity();
        entity.setOperation(record.getAction());
        entity.setOperationType(record.getOperationType() == null ? "" : record.getOperationType().name());
        entity.setBusinessId(record.getBusinessId());
        entity.setDetail(record.getDetail());
        entity.setSuccess(record.isSuccess());
        entity.setErrorMessage(record.getErrorMessage());
        entity.setTraceId(record.getTraceId());
        entity.setReqid(record.getReqid());
        entity.setRequestMethod(record.getHttpMethod());
        entity.setRequestUri(record.getPath());
        entity.setRequestTime(record.getDurationMs());
        entity.setUserAgent(record.getUserAgent());
        entity.setIp(record.getClientIp());
        entity.setCreatorName(record.getOperator());
        entity.setCreateTime(record.getTimestamp() == null ? Instant.now() : record.getTimestamp());
        mapper.insert(entity);
    }
}
