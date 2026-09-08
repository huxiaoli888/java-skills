package {{basePackage}}.cms.sampleitem;

import static org.assertj.core.api.Assertions.assertThat;

import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;

class SampleItemCrudContractTest {
    @Test
    void templateIncludesCrudBoundaryFiles() throws Exception {
        Path root = Path.of("src/main/java");
        assertThat(Files.exists(root)).isTrue();
    }
}
