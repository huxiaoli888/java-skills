package com.chaken.ai.test.production.config;

import com.chaken.ai.test.common.log.service.OperationAuditService;
import com.chaken.ai.test.common.security.ratelimit.RateLimiter;
import com.chaken.ai.test.production.audit.JdbcOperationAuditService;
import com.chaken.ai.test.production.audit.JdbcTemplateOperationAuditRecordRepository;
import com.chaken.ai.test.production.audit.OperationAuditRecordRepository;
import com.chaken.ai.test.production.idempotency.JdbcIdempotencyRecordRepository;
import com.chaken.ai.test.production.idempotency.JdbcIdempotencyService;
import com.chaken.ai.test.production.idempotency.JdbcTemplateIdempotencyRecordRepository;
import com.chaken.ai.test.production.redis.RedisRateLimiter;
import com.chaken.ai.test.production.redis.RedisReplayRequestStore;
import com.chaken.ai.test.security.idempotency.IdempotencyService;
import com.chaken.ai.test.security.replay.ReplayRequestStore;
import java.time.Clock;
import org.springframework.boot.autoconfigure.condition.ConditionalOnBean;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.jdbc.core.JdbcTemplate;

@Configuration
@EnableConfigurationProperties(ProductionReplacementProperties.class)
@ConditionalOnProperty(prefix = "app.production.replacement", name = "enabled", havingValue = "true")
public class ProductionReplacementAutoConfiguration {
    @Bean
    @ConditionalOnMissingBean
    Clock systemClock() {
        return Clock.systemUTC();
    }

    @Bean
    @ConditionalOnBean(StringRedisTemplate.class)
    @ConditionalOnMissingBean(ReplayRequestStore.class)
    ReplayRequestStore redisReplayRequestStore(
            StringRedisTemplate redisTemplate,
            ProductionReplacementProperties properties) {
        return new RedisReplayRequestStore(redisTemplate, properties.getRedisKeyPrefix());
    }

    @Bean
    @ConditionalOnBean(StringRedisTemplate.class)
    @ConditionalOnMissingBean(RateLimiter.class)
    RateLimiter redisRateLimiter(
            StringRedisTemplate redisTemplate,
            ProductionReplacementProperties properties) {
        return new RedisRateLimiter(redisTemplate, properties.getRedisKeyPrefix());
    }

    @Bean
    @ConditionalOnBean(JdbcTemplate.class)
    @ConditionalOnMissingBean(JdbcIdempotencyRecordRepository.class)
    JdbcIdempotencyRecordRepository jdbcIdempotencyRecordRepository(JdbcTemplate jdbcTemplate) {
        return new JdbcTemplateIdempotencyRecordRepository(jdbcTemplate);
    }

    @Bean
    @ConditionalOnBean(JdbcIdempotencyRecordRepository.class)
    @ConditionalOnMissingBean(IdempotencyService.class)
    IdempotencyService jdbcIdempotencyService(
            JdbcIdempotencyRecordRepository repository,
            Clock clock,
            ProductionReplacementProperties properties) {
        return new JdbcIdempotencyService(repository, clock, properties.getIdempotencyTtl());
    }

    @Bean
    @ConditionalOnBean(JdbcTemplate.class)
    @ConditionalOnMissingBean(OperationAuditRecordRepository.class)
    OperationAuditRecordRepository operationAuditRecordRepository(JdbcTemplate jdbcTemplate) {
        return new JdbcTemplateOperationAuditRecordRepository(jdbcTemplate);
    }

    @Bean
    @ConditionalOnBean(OperationAuditRecordRepository.class)
    @ConditionalOnMissingBean(OperationAuditService.class)
    OperationAuditService jdbcOperationAuditService(OperationAuditRecordRepository repository) {
        return new JdbcOperationAuditService(repository);
    }
}
