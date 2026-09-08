package com.chaken.ai.test.common.security.file;

import com.chaken.ai.test.common.config.FileUploadSecurityProperties;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

class FileUploadSecurityPolicyTest {
    @Test
    void shouldRejectDisallowedTypeAndOversizedFile() {
        FileUploadSecurityProperties properties = new FileUploadSecurityProperties();
        properties.setMaxBytes(10);
        properties.setAllowedExtensions(List.of("png"));
        properties.setAllowedContentTypes(List.of("image/png"));
        FileUploadSecurityPolicy policy = new FileUploadSecurityPolicy(properties);

        assertThat(policy.isAllowed("a.png", "image/png", 10)).isTrue();
        assertThat(policy.isAllowed("a.exe", "application/octet-stream", 1)).isFalse();
        assertThat(policy.isAllowed("a.png", "image/png", 11)).isFalse();
    }
}
