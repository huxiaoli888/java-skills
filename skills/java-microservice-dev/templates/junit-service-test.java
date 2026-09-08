package {{basePackage}}.service;

import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

class {{serviceClass}}Test {

    @Test
    void {{methodName}}_returnsExpectedResult() {
        // Arrange
        {{serviceClass}} service = new {{serviceClass}}();

        // Act
        // Object result = service.{{methodName}}(...);

        // Assert
        assertThat(service).isNotNull();
    }
}
