package com.chaken.ai.test.cms.config;

import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;

import static org.assertj.core.api.Assertions.assertThat;

class ProductionConfigurationPolicyTest {
    @Test
    void productionConfigShouldNotExposeAllActuatorEndpointsOrDefaultSecrets() throws IOException {
        String text = readResource("/application-prod.yml");

        assertThat(text).doesNotContain("include: \"*\"");
        assertThat(text).doesNotContain("include: '*'");
        assertThat(text).doesNotContain("change-me");
        assertThat(text).doesNotContain("dev-cms-token");
        assertThat(text).doesNotContain("test-cms-token");
    }

    private String readResource(String path) throws IOException {
        try (InputStream inputStream = getClass().getResourceAsStream(path)) {
            assertThat(inputStream).as(path).isNotNull();
            return new String(inputStream.readAllBytes(), StandardCharsets.UTF_8);
        }
    }
}
