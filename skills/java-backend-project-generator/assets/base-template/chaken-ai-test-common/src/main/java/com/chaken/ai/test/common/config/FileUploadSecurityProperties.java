package com.chaken.ai.test.common.config;

import java.util.ArrayList;
import java.util.List;
import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "chaken.security.file-upload")
public class FileUploadSecurityProperties {
    private boolean enabled = true;
    private long maxBytes = 10 * 1024 * 1024L;
    private List<String> allowedContentTypes = new ArrayList<>(List.of("image/png", "image/jpeg", "application/pdf"));
    private List<String> allowedExtensions = new ArrayList<>(List.of("png", "jpg", "jpeg", "pdf"));

    public boolean isEnabled() {
        return enabled;
    }

    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }

    public long getMaxBytes() {
        return maxBytes;
    }

    public void setMaxBytes(long maxBytes) {
        this.maxBytes = maxBytes;
    }

    public List<String> getAllowedContentTypes() {
        return allowedContentTypes;
    }

    public void setAllowedContentTypes(List<String> allowedContentTypes) {
        this.allowedContentTypes = allowedContentTypes == null ? new ArrayList<>() : allowedContentTypes;
    }

    public List<String> getAllowedExtensions() {
        return allowedExtensions;
    }

    public void setAllowedExtensions(List<String> allowedExtensions) {
        this.allowedExtensions = allowedExtensions == null ? new ArrayList<>() : allowedExtensions;
    }
}
