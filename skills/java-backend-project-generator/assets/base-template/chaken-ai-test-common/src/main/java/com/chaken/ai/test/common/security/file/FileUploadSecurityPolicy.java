package com.chaken.ai.test.common.security.file;

import com.chaken.ai.test.common.config.FileUploadSecurityProperties;
import java.util.List;
import java.util.Locale;

public class FileUploadSecurityPolicy {
    private final FileUploadSecurityProperties properties;

    public FileUploadSecurityPolicy(FileUploadSecurityProperties properties) {
        this.properties = properties;
    }

    public boolean isAllowed(String filename, String contentType, long size) {
        if (!properties.isEnabled()) {
            return true;
        }
        long maxBytes = properties.getMaxBytes();
        if (size < 0 || size > maxBytes) {
            return false;
        }
        return isAllowedContentType(contentType) && isAllowedExtension(filename);
    }

    private boolean isAllowedContentType(String contentType) {
        if (contentType == null || contentType.isBlank()) {
            return false;
        }
        List<String> allowedContentTypes = properties.getAllowedContentTypes();
        return allowedContentTypes.contains(contentType.toLowerCase(Locale.ROOT));
    }

    private boolean isAllowedExtension(String filename) {
        if (filename == null || filename.isBlank()) {
            return false;
        }
        int dot = filename.lastIndexOf('.');
        if (dot < 0 || dot == filename.length() - 1) {
            return false;
        }
        String extension = filename.substring(dot + 1).toLowerCase(Locale.ROOT);
        List<String> allowedExtensions = properties.getAllowedExtensions();
        return allowedExtensions.contains(extension);
    }
}
