package {{basePackage}}.production.config;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;

class ProductionReplacementAutoConfigurationContractTest {
    @Test
    void propertiesDefaultToDisabledUntilProductionExplicitlyEnablesThem() {
        ProductionReplacementProperties properties = new ProductionReplacementProperties();

        assertThat(properties.isEnabled()).isFalse();
        assertThat(properties.getRedisKeyPrefix()).isEqualTo("app");
        assertThat(properties.getIdempotencyTtl()).isPositive();
    }
}
