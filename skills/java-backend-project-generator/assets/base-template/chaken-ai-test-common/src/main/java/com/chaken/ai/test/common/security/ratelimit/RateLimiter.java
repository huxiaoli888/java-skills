package com.chaken.ai.test.common.security.ratelimit;

import java.time.Duration;

public interface RateLimiter {
    boolean tryAcquire(String key, int permits, Duration window);
}
