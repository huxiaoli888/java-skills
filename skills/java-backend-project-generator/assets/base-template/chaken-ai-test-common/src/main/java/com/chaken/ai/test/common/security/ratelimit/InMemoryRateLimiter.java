package com.chaken.ai.test.common.security.ratelimit;

import java.time.Duration;
import java.util.Iterator;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class InMemoryRateLimiter implements RateLimiter {
    private final Map<String, WindowCounter> counters = new ConcurrentHashMap<>();

    @Override
    public boolean tryAcquire(String key, int permits, Duration window) {
        if (permits <= 0) {
            return false;
        }
        long now = System.currentTimeMillis();
        long windowMillis = Math.max(1000L, window.toMillis());
        cleanup(now);
        WindowCounter counter = counters.compute(key, (ignored, current) -> {
            if (current == null || now >= current.expiresAt) {
                return new WindowCounter(now + windowMillis, 1);
            }
            current.count++;
            return current;
        });
        return counter.count <= permits;
    }

    private void cleanup(long now) {
        if (counters.size() < 1024) {
            return;
        }
        Iterator<Map.Entry<String, WindowCounter>> iterator = counters.entrySet().iterator();
        while (iterator.hasNext()) {
            if (now >= iterator.next().getValue().expiresAt) {
                iterator.remove();
            }
        }
    }

    private static final class WindowCounter {
        private final long expiresAt;
        private int count;

        private WindowCounter(long expiresAt, int count) {
            this.expiresAt = expiresAt;
            this.count = count;
        }
    }
}
