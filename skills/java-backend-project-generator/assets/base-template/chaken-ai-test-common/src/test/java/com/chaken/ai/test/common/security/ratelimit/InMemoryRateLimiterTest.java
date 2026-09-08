package com.chaken.ai.test.common.security.ratelimit;

import org.junit.jupiter.api.Test;

import java.time.Duration;

import static org.assertj.core.api.Assertions.assertThat;

class InMemoryRateLimiterTest {
    @Test
    void shouldRejectRequestsOverWindowLimit() {
        InMemoryRateLimiter limiter = new InMemoryRateLimiter();

        assertThat(limiter.tryAcquire("login:user-1", 1, Duration.ofMinutes(1))).isTrue();
        assertThat(limiter.tryAcquire("login:user-1", 1, Duration.ofMinutes(1))).isFalse();
    }
}
