package com.chaken.ai.test.sdk.security.config;

import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "chaken.sdk.security")
public class SdkSecurityProperties {
    private boolean signatureEnabled = true;
    private Duration replayWindow = Duration.ofMinutes(5);
    private String defaultApiKey = "test-api-key";
    private String defaultSecret = "change-me";
    private List<String> authExcludePaths = new ArrayList<>();
    private List<String> udidExcludePaths = new ArrayList<>();

    public boolean isSignatureEnabled() {
        return signatureEnabled;
    }

    public void setSignatureEnabled(boolean signatureEnabled) {
        this.signatureEnabled = signatureEnabled;
    }

    public Duration getReplayWindow() {
        return replayWindow;
    }

    public void setReplayWindow(Duration replayWindow) {
        this.replayWindow = replayWindow;
    }

    public String getDefaultApiKey() {
        return defaultApiKey;
    }

    public void setDefaultApiKey(String defaultApiKey) {
        this.defaultApiKey = defaultApiKey;
    }

    public String getDefaultSecret() {
        return defaultSecret;
    }

    public void setDefaultSecret(String defaultSecret) {
        this.defaultSecret = defaultSecret;
    }

    public List<String> getAuthExcludePaths() {
        return authExcludePaths;
    }

    public void setAuthExcludePaths(List<String> authExcludePaths) {
        this.authExcludePaths = authExcludePaths == null ? new ArrayList<>() : authExcludePaths;
    }

    public List<String> getUdidExcludePaths() {
        return udidExcludePaths;
    }

    public void setUdidExcludePaths(List<String> udidExcludePaths) {
        this.udidExcludePaths = udidExcludePaths == null ? new ArrayList<>() : udidExcludePaths;
    }
}
