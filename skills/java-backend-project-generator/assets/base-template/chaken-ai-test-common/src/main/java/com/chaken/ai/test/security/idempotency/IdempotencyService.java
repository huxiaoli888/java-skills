package com.chaken.ai.test.security.idempotency;

public interface IdempotencyService {
    IdempotencyDecision check(
            String ownerId,
            String requestFingerprint,
            String businessType,
            String businessKey);

    void saveResult(
            String ownerId,
            String businessType,
            String businessKey,
            String responseSnapshot);
}
