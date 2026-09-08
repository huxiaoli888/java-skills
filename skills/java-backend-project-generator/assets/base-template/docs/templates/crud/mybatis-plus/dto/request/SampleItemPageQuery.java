package {{basePackage}}.cms.sampleitem.dto.request;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@Schema(description = "Sample item page query")
public class SampleItemPageQuery {
    @Schema(description = "Page number, starts from 1")
    @Min(value = 1, message = "{page.min}")
    private int page = 1;

    @Schema(description = "Page size")
    @Min(value = 1, message = "{pageSize.min}")
    @Max(value = 200, message = "{pageSize.max}")
    private int pageSize = 20;

    @Schema(description = "Item name fuzzy query")
    @Size(max = 128, message = "{sampleItem.name.size}")
    private String name;

    @Schema(description = "Sort rule, for example createTime,desc")
    private String sort;
}
