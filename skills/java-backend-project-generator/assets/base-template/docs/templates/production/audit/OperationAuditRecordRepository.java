package com.chaken.ai.test.production.audit;

import com.chaken.ai.test.common.log.model.OperationAuditRecord;

public interface OperationAuditRecordRepository {
    void insert(OperationAuditRecord record);
}
