package com.chaken.ai.test.production.audit;

import com.chaken.ai.test.common.log.model.OperationAuditRecord;
import com.chaken.ai.test.common.log.service.OperationAuditService;

public class JdbcOperationAuditService implements OperationAuditService {
    private final OperationAuditRecordRepository repository;

    public JdbcOperationAuditService(OperationAuditRecordRepository repository) {
        this.repository = repository;
    }

    @Override
    public void save(OperationAuditRecord record) {
        repository.insert(record);
    }
}
