package com.chaken.ai.test.common.config;

import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
@EnableConfigurationProperties(ApiCorsProperties.class)
public class ApiCorsConfiguration implements WebMvcConfigurer {
    private final ApiCorsProperties properties;

    public ApiCorsConfiguration(ApiCorsProperties properties) {
        this.properties = properties;
    }

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        if (!properties.isEnabled()) {
            return;
        }
        validate();

        CorsRegistration registration = registry.addMapping(properties.getPathPattern());
        if (!properties.getAllowedOrigins().isEmpty()) {
            registration.allowedOrigins(properties.getAllowedOrigins().toArray(String[]::new));
        }
        if (!properties.getAllowedOriginPatterns().isEmpty()) {
            registration.allowedOriginPatterns(properties.getAllowedOriginPatterns().toArray(String[]::new));
        }
        registration.allowedMethods(properties.getAllowedMethods().toArray(String[]::new));
        registration.allowedHeaders(properties.getAllowedHeaders().toArray(String[]::new));
        registration.exposedHeaders(properties.getExposedHeaders().toArray(String[]::new));
        registration.allowCredentials(properties.isAllowCredentials());
        registration.maxAge(properties.getMaxAge());
    }

    private void validate() {
        if (!properties.isAllowCredentials()) {
            return;
        }
        // 允许携带凭证时禁止使用通配 origin。
        if (properties.getAllowedOrigins().contains("*") || properties.getAllowedOriginPatterns().contains("*")) {
            throw new IllegalStateException("CORS 允许携带凭证时不能使用通配 origin");
        }
    }
}
