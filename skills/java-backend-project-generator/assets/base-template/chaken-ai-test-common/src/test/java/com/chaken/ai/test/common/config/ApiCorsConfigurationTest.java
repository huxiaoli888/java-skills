package com.chaken.ai.test.common.config;

import org.junit.jupiter.api.Test;
import org.springframework.web.servlet.config.annotation.CorsRegistry;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThatThrownBy;

class ApiCorsConfigurationTest {
    @Test
    void wildcardOriginWithCredentialsShouldBeRejected() {
        ApiCorsProperties properties = new ApiCorsProperties();
        properties.setAllowCredentials(true);
        properties.setAllowedOrigins(List.of("*"));

        ApiCorsConfiguration configuration = new ApiCorsConfiguration(properties);

        assertThatThrownBy(() -> configuration.addCorsMappings(new CorsRegistry()))
                .isInstanceOf(IllegalStateException.class);
    }
}
