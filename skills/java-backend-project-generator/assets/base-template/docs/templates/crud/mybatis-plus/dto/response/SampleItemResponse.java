package {{basePackage}}.cms.sampleitem.dto.response;

import io.swagger.v3.oas.annotations.media.Schema;
import java.time.Instant;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@Schema(description = "Sample item response")
public class SampleItemResponse {
    @Schema(description = "ID")
    private Long id;

    @Schema(description = "Item name")
    private String name;

    @Schema(description = "Item remark")
    private String remark;

    @Schema(description = "Optimistic lock version")
    private Long version;

    @Schema(description = "Create time")
    private Instant createTime;

    @Schema(description = "Modify time")
    private Instant modifyTime;
}
