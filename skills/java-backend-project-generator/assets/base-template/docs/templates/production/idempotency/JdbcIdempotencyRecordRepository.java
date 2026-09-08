package com.chaken.ai.test.production.idempotency;

import com.chaken.ai.test.security.idempotency.IdempotencyRecord;
import java.time.Instant;
import java.util.Optional;

public interface JdbcIdempotencyRecordRepository {
    boolean insertProcessing(IdempotencyRecord record);

    Optional<IdempotencyRecord> findActive(String ownerId, String businessType, String businessKey, Instant now);

    void markSucceeded(String ownerId, String businessType, String businessKey, String responseSnapshot);
}
