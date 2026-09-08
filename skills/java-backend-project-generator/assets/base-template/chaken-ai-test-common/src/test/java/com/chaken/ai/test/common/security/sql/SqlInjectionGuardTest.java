package com.chaken.ai.test.common.security.sql;

import org.junit.jupiter.api.Test;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

class SqlInjectionGuardTest {
    @Test
    void shouldDetectObviousSqlInjectionMarkers() {
        SqlInjectionGuard guard = new SqlInjectionGuard(List.of("(?i).*\\bor\\b\\s+'1'='1.*"));

        assertThat(guard.hasInjectionRisk("name' or '1'='1")).isTrue();
        assertThat(guard.hasInjectionRisk("normal keyword")).isFalse();
    }
}
