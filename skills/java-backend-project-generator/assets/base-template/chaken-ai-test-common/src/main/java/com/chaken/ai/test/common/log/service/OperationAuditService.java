package com.chaken.ai.test.common.log.service;

import com.chaken.ai.test.common.log.model.OperationAuditRecord;

public interface OperationAuditService {
    void save(OperationAuditRecord record);
}
