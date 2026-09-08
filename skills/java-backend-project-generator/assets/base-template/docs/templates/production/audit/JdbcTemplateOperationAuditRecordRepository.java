package com.chaken.ai.test.production.audit;

import com.chaken.ai.test.common.log.model.OperationAuditRecord;
import java.sql.Timestamp;
import java.time.Instant;
import org.springframework.jdbc.core.JdbcTemplate;

public class JdbcTemplateOperationAuditRecordRepository implements OperationAuditRecordRepository {
    private final JdbcTemplate jdbcTemplate;

    public JdbcTemplateOperationAuditRecordRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @Override
    public void insert(OperationAuditRecord record) {
        jdbcTemplate.update(
                """
                insert into operation_audit_log (
                    reqid, trace_id, operator, operation_type, operation_name,
                    business_id, success, code, message, client_ip, duration_ms, create_time
                ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                value(record.getReqid()),
                value(record.getTraceId()),
                value(record.getOperator()),
                record.getOperationType() == null ? "UNKNOWN" : record.getOperationType().name(),
                value(record.getAction()),
                value(record.getBusinessId()),
                record.isSuccess() ? 1 : 0,
                record.isSuccess() ? "" : "AC9999",
                value(record.getErrorMessage()),
                value(record.getClientIp()),
                record.getDurationMs(),
                Timestamp.from(record.getTimestamp() == null ? Instant.now() : record.getTimestamp()));
    }

    private String value(String text) {
        return text == null ? "" : text;
    }
}
