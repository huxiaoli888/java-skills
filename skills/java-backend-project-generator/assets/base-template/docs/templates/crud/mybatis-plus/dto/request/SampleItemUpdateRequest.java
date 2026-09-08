package {{basePackage}}.cms.sampleitem.dto.request;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@Schema(description = "Update sample item request")
public class SampleItemUpdateRequest {
    @Schema(description = "Item name", requiredMode = Schema.RequiredMode.REQUIRED)
    @NotBlank(message = "{sampleItem.name.required}")
    @Size(max = 128, message = "{sampleItem.name.size}")
    private String name;

    @Schema(description = "Item remark")
    @Size(max = 512, message = "{sampleItem.remark.size}")
    private String remark;

    @Schema(description = "Optimistic lock version", requiredMode = Schema.RequiredMode.REQUIRED)
    @NotNull(message = "{sampleItem.version.required}")
    private Long version;
}
