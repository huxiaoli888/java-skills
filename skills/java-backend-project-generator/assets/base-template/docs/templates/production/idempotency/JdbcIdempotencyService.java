package com.chaken.ai.test.production.idempotency;

import com.chaken.ai.test.security.idempotency.IdempotencyDecision;
import com.chaken.ai.test.security.idempotency.IdempotencyRecord;
import com.chaken.ai.test.security.idempotency.IdempotencyService;
import com.chaken.ai.test.security.idempotency.IdempotencyStatus;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;

public class JdbcIdempotencyService implements IdempotencyService {
    private final JdbcIdempotencyRecordRepository repository;
    private final Clock clock;
    private final Duration ttl;

    public JdbcIdempotencyService(JdbcIdempotencyRecordRepository repository, Clock clock, Duration ttl) {
        this.repository = repository;
        this.clock = clock;
        this.ttl = ttl;
    }

    @Override
    public IdempotencyDecision check(String ownerId, String requestFingerprint, String businessType, String businessKey) {
        Instant now = clock.instant();
        IdempotencyRecord record = new IdempotencyRecord();
        record.setOwnerId(ownerId);
        record.setRequestFingerprint(requestFingerprint);
        record.setBusinessType(businessType);
        record.setBusinessKey(businessKey);
        record.setStatus(IdempotencyStatus.PROCESSING);
        record.setCreatedTime(now);
        record.setExpireTime(now.plus(ttl));
        if (repository.insertProcessing(record)) {
            return IdempotencyDecision.FIRST_REQUEST;
        }
        return repository.findActive(ownerId, businessType, businessKey, now)
                .map(existing -> requestFingerprint.equals(existing.getRequestFingerprint())
                        ? IdempotencyDecision.REPLAY_SAME_REQUEST
                        : IdempotencyDecision.CONFLICT_DIFFERENT_REQUEST)
                .orElse(IdempotencyDecision.FIRST_REQUEST);
    }

    @Override
    public void saveResult(String ownerId, String businessType, String businessKey, String responseSnapshot) {
        repository.markSucceeded(ownerId, businessType, businessKey, responseSnapshot);
    }
}
