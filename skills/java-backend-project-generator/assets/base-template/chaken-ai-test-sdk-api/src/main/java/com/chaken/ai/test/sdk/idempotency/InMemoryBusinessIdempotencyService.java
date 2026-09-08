package com.chaken.ai.test.sdk.idempotency;

import com.chaken.ai.test.security.idempotency.IdempotencyDecision;
import com.chaken.ai.test.security.idempotency.IdempotencyService;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import org.springframework.stereotype.Service;

@Service
public class InMemoryBusinessIdempotencyService implements IdempotencyService {
    private final ConcurrentMap<String, String> fingerprints = new ConcurrentHashMap<>();
    private final ConcurrentMap<String, String> responseSnapshots = new ConcurrentHashMap<>();

    @Override
    public IdempotencyDecision check(
            String ownerId,
            String requestFingerprint,
            String businessType,
            String businessKey) {
        String key = key(ownerId, businessType, businessKey);
        String existingFingerprint = fingerprints.putIfAbsent(key, requestFingerprint);
        if (existingFingerprint == null) {
            return IdempotencyDecision.FIRST_REQUEST;
        }
        if (existingFingerprint.equals(requestFingerprint)) {
            return IdempotencyDecision.REPLAY_SAME_REQUEST;
        }
        return IdempotencyDecision.CONFLICT_DIFFERENT_REQUEST;
    }

    @Override
    public void saveResult(
            String ownerId,
            String businessType,
            String businessKey,
            String responseSnapshot) {
        responseSnapshots.put(key(ownerId, businessType, businessKey), responseSnapshot);
    }

    public String resultSnapshot(String ownerId, String businessType, String businessKey) {
        return responseSnapshots.get(key(ownerId, businessType, businessKey));
    }

    private String key(String ownerId, String businessType, String businessKey) {
        return ownerId + ":" + businessType + ":" + businessKey;
    }
}
