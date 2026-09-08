package com.chaken.ai.test.common.log.service;

import com.chaken.ai.test.common.log.model.OperationAuditRecord;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

@Service
public class LoggingOperationAuditService implements OperationAuditService {
    private static final Logger log = LoggerFactory.getLogger(LoggingOperationAuditService.class);

    @Override
    public void save(OperationAuditRecord record) {
        log.info(
                "operationAudit reqid={} traceId={} operator={} type={} action={} businessId={} success={} durationMs={} method={} path={} clientIp={} userAgent={} errorMessage={} detail={}",
                record.getReqid(),
                record.getTraceId(),
                record.getOperator(),
                record.getOperationType(),
                record.getAction(),
                record.getBusinessId(),
                record.isSuccess(),
                record.getDurationMs(),
                record.getHttpMethod(),
                record.getPath(),
                record.getClientIp(),
                value(record.getUserAgent()),
                value(record.getErrorMessage()),
                value(record.getDetail()));
    }

    private String value(String value) {
        return value == null ? "" : value;
    }
}
