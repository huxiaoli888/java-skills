package com.chaken.ai.test.common.config;

import java.util.ArrayList;
import java.util.List;
import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "chaken.security.sql-injection")
public class SqlInjectionProperties {
    private boolean enabled = true;
    private boolean checkQueryParameters = true;
    private boolean checkFormParameters = false;
    private List<String> excludePaths = new ArrayList<>();
    private List<String> blockedPatterns = new ArrayList<>(List.of(
            "(?i).*\\b(union\\s+select|select\\s+.+\\s+from|insert\\s+into|update\\s+.+\\s+set|delete\\s+from|drop\\s+table|alter\\s+table|truncate\\s+table)\\b.*",
            "(?i).*('|\")\\s*(or|and)\\s+('|\")?\\w+('|\")?\\s*=\\s*('|\")?\\w+('|\")?.*",
            ".*(--|/\\*|\\*/|;\\s*$).*"));

    public boolean isEnabled() {
        return enabled;
    }

    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }

    public boolean isCheckQueryParameters() {
        return checkQueryParameters;
    }

    public void setCheckQueryParameters(boolean checkQueryParameters) {
        this.checkQueryParameters = checkQueryParameters;
    }

    public boolean isCheckFormParameters() {
        return checkFormParameters;
    }

    public void setCheckFormParameters(boolean checkFormParameters) {
        this.checkFormParameters = checkFormParameters;
    }

    public List<String> getExcludePaths() {
        return excludePaths;
    }

    public void setExcludePaths(List<String> excludePaths) {
        this.excludePaths = excludePaths == null ? new ArrayList<>() : excludePaths;
    }

    public List<String> getBlockedPatterns() {
        return blockedPatterns;
    }

    public void setBlockedPatterns(List<String> blockedPatterns) {
        this.blockedPatterns = blockedPatterns == null ? new ArrayList<>() : blockedPatterns;
    }
}
