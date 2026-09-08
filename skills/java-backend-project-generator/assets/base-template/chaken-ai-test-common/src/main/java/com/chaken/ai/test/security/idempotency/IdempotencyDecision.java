package com.chaken.ai.test.security.idempotency;

public enum IdempotencyDecision {
    FIRST_REQUEST,
    REPLAY_SAME_REQUEST,
    CONFLICT_DIFFERENT_REQUEST
}
