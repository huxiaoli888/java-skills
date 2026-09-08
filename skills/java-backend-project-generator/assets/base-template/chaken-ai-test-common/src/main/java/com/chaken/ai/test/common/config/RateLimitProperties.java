package com.chaken.ai.test.common.config;

import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "chaken.security.rate-limit")
public class RateLimitProperties {
    private boolean enabled = true;
    private int defaultPermits = 120;
    private Duration defaultWindow = Duration.ofMinutes(1);
    private List<String> identityHeaders = new ArrayList<>(List.of("x-api-key", "x-udid"));
    private List<String> excludePaths = new ArrayList<>();
    private List<RateLimitRule> rules = new ArrayList<>();

    public boolean isEnabled() {
        return enabled;
    }

    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }

    public int getDefaultPermits() {
        return defaultPermits;
    }

    public void setDefaultPermits(int defaultPermits) {
        this.defaultPermits = defaultPermits;
    }

    public Duration getDefaultWindow() {
        return defaultWindow;
    }

    public void setDefaultWindow(Duration defaultWindow) {
        this.defaultWindow = defaultWindow;
    }

    public List<String> getIdentityHeaders() {
        return identityHeaders;
    }

    public void setIdentityHeaders(List<String> identityHeaders) {
        this.identityHeaders = identityHeaders == null ? new ArrayList<>() : identityHeaders;
    }

    public List<String> getExcludePaths() {
        return excludePaths;
    }

    public void setExcludePaths(List<String> excludePaths) {
        this.excludePaths = excludePaths == null ? new ArrayList<>() : excludePaths;
    }

    public List<RateLimitRule> getRules() {
        return rules;
    }

    public void setRules(List<RateLimitRule> rules) {
        this.rules = rules == null ? new ArrayList<>() : rules;
    }

    public static class RateLimitRule {
        private String pathPattern = "/**";
        private int permits = 120;
        private Duration window = Duration.ofMinutes(1);

        public String getPathPattern() {
            return pathPattern;
        }

        public void setPathPattern(String pathPattern) {
            this.pathPattern = pathPattern;
        }

        public int getPermits() {
            return permits;
        }

        public void setPermits(int permits) {
            this.permits = permits;
        }

        public Duration getWindow() {
            return window;
        }

        public void setWindow(Duration window) {
            this.window = window;
        }
    }
}
