package com.chaken.ai.test.production.redis;

import com.chaken.ai.test.common.security.ratelimit.RateLimiter;
import java.time.Duration;
import java.util.List;
import org.springframework.data.redis.core.StringRedisTemplate;

public class RedisRateLimiter implements RateLimiter {
    private final StringRedisTemplate redisTemplate;
    private final String keyPrefix;

    public RedisRateLimiter(StringRedisTemplate redisTemplate, String keyPrefix) {
        this.redisTemplate = redisTemplate;
        this.keyPrefix = keyPrefix;
    }

    @Override
    public boolean tryAcquire(String key, int permits, Duration window) {
        String redisKey = keyPrefix + ":rate:" + key;
        Long count = redisTemplate.opsForValue().increment(redisKey);
        if (count != null && count == 1L) {
            redisTemplate.expire(redisKey, window);
        }
        return count != null && count <= permits;
    }
}
