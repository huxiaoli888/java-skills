package {{basePackage}}.cms.sampleitem.entity;

import {{basePackage}}.common.persistence.BaseEntity;
import com.baomidou.mybatisplus.annotation.TableName;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@Schema(description = "Sample item persistence entity")
@TableName("sample_item")
public class SampleItemEntity extends BaseEntity {
    @Schema(description = "Item name")
    private String name;

    @Schema(description = "Item remark")
    private String remark;
}
