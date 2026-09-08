package com.chaken.ai.test.production.redis;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assumptions.assumeTrue;

import java.time.Duration;
import org.junit.jupiter.api.Test;
import org.springframework.data.redis.connection.RedisStandaloneConfiguration;
import org.springframework.data.redis.connection.lettuce.LettuceConnectionFactory;
import org.springframework.data.redis.core.StringRedisTemplate;

class RedisReplayAndRateLimitIntegrationTest {
    @Test
    void redisReplayAndRateLimitUseDistributedKeys() {
        String host = System.getenv("TEST_REDIS_HOST");
        assumeTrue(host != null && !host.isBlank(), "set TEST_REDIS_HOST to run Redis integration test");

        RedisStandaloneConfiguration configuration = new RedisStandaloneConfiguration(host);
        String port = System.getenv("TEST_REDIS_PORT");
        if (port != null && !port.isBlank()) {
            configuration.setPort(Integer.parseInt(port));
        }
        LettuceConnectionFactory factory = new LettuceConnectionFactory(configuration);
        factory.afterPropertiesSet();
        try {
            StringRedisTemplate redisTemplate = new StringRedisTemplate(factory);
            RedisReplayRequestStore replayRequestStore = new RedisReplayRequestStore(redisTemplate, "integration");
            RedisRateLimiter rateLimiter = new RedisRateLimiter(redisTemplate, "integration");

            assertThat(replayRequestStore.saveIfAbsent("replay-subject", "reqid-1", Duration.ofMinutes(1))).isTrue();
            assertThat(replayRequestStore.saveIfAbsent("replay-subject", "reqid-1", Duration.ofMinutes(1))).isFalse();
            assertThat(rateLimiter.tryAcquire("path:user", 1, Duration.ofMinutes(1))).isTrue();
            assertThat(rateLimiter.tryAcquire("path:user", 1, Duration.ofMinutes(1))).isFalse();
        } finally {
            factory.destroy();
        }
    }
}
