package com.chaken.ai.test.common.config;

import com.chaken.ai.test.common.security.ratelimit.InMemoryRateLimiter;
import com.chaken.ai.test.common.security.ratelimit.RateLimitFilter;
import com.chaken.ai.test.common.security.ratelimit.RateLimiter;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
@EnableConfigurationProperties(RateLimitProperties.class)
public class RateLimitConfiguration {
    @Bean
    public RateLimiter rateLimiter() {
        return new InMemoryRateLimiter();
    }

    @Bean
    public FilterRegistrationBean<RateLimitFilter> rateLimitFilterRegistration(
            RateLimitProperties properties,
            RateLimiter rateLimiter) {
        FilterRegistrationBean<RateLimitFilter> registration = new FilterRegistrationBean<>();
        registration.setFilter(new RateLimitFilter(properties, rateLimiter));
        registration.setOrder(Integer.MIN_VALUE + 8);
        registration.addUrlPatterns("/*");
        return registration;
    }
}
