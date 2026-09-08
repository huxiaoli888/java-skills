package com.chaken.ai.test.cms.security;

import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "chaken.cms.security")
public class CmsSecurityProperties {
    private boolean enabled = true;
    private boolean signatureEnabled = true;
    private Duration replayWindow = Duration.ofMinutes(5);
    private Duration tokenTtl = Duration.ofHours(12);
    private String defaultSignSecret = "change-me";
    private List<String> authExcludePaths = new ArrayList<>();
    private List<String> udidExcludePaths = new ArrayList<>();

    public boolean isEnabled() {
        return enabled;
    }

    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }

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

    public Duration getTokenTtl() {
        return tokenTtl;
    }

    public void setTokenTtl(Duration tokenTtl) {
        this.tokenTtl = tokenTtl;
    }

    public String getDefaultSignSecret() {
        return defaultSignSecret;
    }

    public void setDefaultSignSecret(String defaultSignSecret) {
        this.defaultSignSecret = defaultSignSecret;
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
