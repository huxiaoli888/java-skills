package com.chaken.ai.test.common.config;

import java.util.ArrayList;
import java.util.List;
import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "chaken.web.cors")
public class ApiCorsProperties {
    private boolean enabled = true;
    private String pathPattern = "/**";
    private List<String> allowedOrigins = new ArrayList<>();
    private List<String> allowedOriginPatterns = new ArrayList<>();
    private List<String> allowedMethods = new ArrayList<>(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));
    private List<String> allowedHeaders = new ArrayList<>(List.of(
            "authorization",
            "accept-language",
            "content-type",
            "x-api-key",
            "x-timestamp",
            "x-reqid",
            "x-sign",
            "x-sign-alg",
            "x-api-version",
            "x-trace-id",
            "x-udid"));
    private List<String> exposedHeaders = new ArrayList<>(List.of("x-trace-id"));
    private boolean allowCredentials = true;
    private long maxAge = 1800;

    public boolean isEnabled() {
        return enabled;
    }

    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }

    public String getPathPattern() {
        return pathPattern;
    }

    public void setPathPattern(String pathPattern) {
        this.pathPattern = pathPattern;
    }

    public List<String> getAllowedOrigins() {
        return allowedOrigins;
    }

    public void setAllowedOrigins(List<String> allowedOrigins) {
        this.allowedOrigins = allowedOrigins == null ? new ArrayList<>() : allowedOrigins;
    }

    public List<String> getAllowedOriginPatterns() {
        return allowedOriginPatterns;
    }

    public void setAllowedOriginPatterns(List<String> allowedOriginPatterns) {
        this.allowedOriginPatterns = allowedOriginPatterns == null ? new ArrayList<>() : allowedOriginPatterns;
    }

    public List<String> getAllowedMethods() {
        return allowedMethods;
    }

    public void setAllowedMethods(List<String> allowedMethods) {
        this.allowedMethods = allowedMethods == null ? new ArrayList<>() : allowedMethods;
    }

    public List<String> getAllowedHeaders() {
        return allowedHeaders;
    }

    public void setAllowedHeaders(List<String> allowedHeaders) {
        this.allowedHeaders = allowedHeaders == null ? new ArrayList<>() : allowedHeaders;
    }

    public List<String> getExposedHeaders() {
        return exposedHeaders;
    }

    public void setExposedHeaders(List<String> exposedHeaders) {
        this.exposedHeaders = exposedHeaders == null ? new ArrayList<>() : exposedHeaders;
    }

    public boolean isAllowCredentials() {
        return allowCredentials;
    }

    public void setAllowCredentials(boolean allowCredentials) {
        this.allowCredentials = allowCredentials;
    }

    public long getMaxAge() {
        return maxAge;
    }

    public void setMaxAge(long maxAge) {
        this.maxAge = maxAge;
    }
}
