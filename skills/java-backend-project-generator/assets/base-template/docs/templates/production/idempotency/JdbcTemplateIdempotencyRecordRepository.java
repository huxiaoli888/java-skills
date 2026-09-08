package com.chaken.ai.test.production.idempotency;

import com.chaken.ai.test.security.idempotency.IdempotencyRecord;
import com.chaken.ai.test.security.idempotency.IdempotencyStatus;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.dao.DuplicateKeyException;
import org.springframework.jdbc.core.JdbcTemplate;

public class JdbcTemplateIdempotencyRecordRepository implements JdbcIdempotencyRecordRepository {
    private static final Logger log = LoggerFactory.getLogger(JdbcTemplateIdempotencyRecordRepository.class);
    private final JdbcTemplate jdbcTemplate;

    public JdbcTemplateIdempotencyRecordRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @Override
    public boolean insertProcessing(IdempotencyRecord record) {
        try {
            jdbcTemplate.update(
                    """
                    insert into api_idempotency_record (
                        owner_id, business_type, business_key, request_fingerprint,
                        status, response_snapshot, created_time, expire_time
                    ) values (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    record.getOwnerId(),
                    record.getBusinessType(),
                    record.getBusinessKey(),
                    record.getRequestFingerprint(),
                    record.getStatus().name(),
                    record.getResponseSnapshot(),
                    Timestamp.from(record.getCreatedTime()),
                    Timestamp.from(record.getExpireTime()));
            return true;
        } catch (DuplicateKeyException ex) {
            log.error("idempotency_record_duplicate ownerId={} businessType={} businessKey={}",
                    record.getOwnerId(), record.getBusinessType(), record.getBusinessKey(), ex);
            return false;
        }
    }

    @Override
    public Optional<IdempotencyRecord> findActive(String ownerId, String businessType, String businessKey, Instant now) {
        return jdbcTemplate.query(
                        """
                        select owner_id, business_type, business_key, request_fingerprint,
                               status, response_snapshot, created_time, expire_time
                        from api_idempotency_record
                        where owner_id = ?
                          and business_type = ?
                          and business_key = ?
                          and expire_time > ?
                        """,
                        (rs, rowNum) -> mapRecord(rs),
                        ownerId,
                        businessType,
                        businessKey,
                        Timestamp.from(now))
                .stream()
                .findFirst();
    }

    @Override
    public void markSucceeded(String ownerId, String businessType, String businessKey, String responseSnapshot) {
        jdbcTemplate.update(
                """
                update api_idempotency_record
                set status = ?, response_snapshot = ?
                where owner_id = ?
                  and business_type = ?
                  and business_key = ?
                """,
                IdempotencyStatus.SUCCEEDED.name(),
                responseSnapshot,
                ownerId,
                businessType,
                businessKey);
    }

    private IdempotencyRecord mapRecord(ResultSet rs) throws SQLException {
        IdempotencyRecord record = new IdempotencyRecord();
        record.setOwnerId(rs.getString("owner_id"));
        record.setBusinessType(rs.getString("business_type"));
        record.setBusinessKey(rs.getString("business_key"));
        record.setRequestFingerprint(rs.getString("request_fingerprint"));
        record.setStatus(IdempotencyStatus.valueOf(rs.getString("status")));
        record.setResponseSnapshot(rs.getString("response_snapshot"));
        record.setCreatedTime(rs.getTimestamp("created_time").toInstant());
        record.setExpireTime(rs.getTimestamp("expire_time").toInstant());
        return record;
    }
}
