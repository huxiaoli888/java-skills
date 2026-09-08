package com.chaken.ai.test.production.redis;

import com.chaken.ai.test.security.replay.ReplayRequestStore;
import java.time.Duration;
import org.springframework.data.redis.core.StringRedisTemplate;

public class RedisReplayRequestStore implements ReplayRequestStore {
    private final StringRedisTemplate redisTemplate;
    private final String keyPrefix;

    public RedisReplayRequestStore(StringRedisTemplate redisTemplate, String keyPrefix) {
        this.redisTemplate = redisTemplate;
        this.keyPrefix = keyPrefix;
    }

    @Override
    public boolean saveIfAbsent(String replaySubject, String reqid, Duration ttl) {
        String key = keyPrefix + ":replay:" + replaySubject + ":" + reqid;
        Boolean saved = redisTemplate.opsForValue().setIfAbsent(key, "1", ttl);
        return Boolean.TRUE.equals(saved);
    }
}
