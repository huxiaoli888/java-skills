package com.chaken.ai.test.common.persistence;

import com.baomidou.mybatisplus.annotation.FieldFill;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.Version;
import java.time.Instant;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public abstract class BaseEntity {
    @TableId(type = IdType.ASSIGN_ID)
    private Long id;

    @TableField(fill = FieldFill.INSERT)
    private String createBy;

    @TableField(fill = FieldFill.INSERT)
    private Instant createTime;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private String modifyBy;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private Instant modifyTime;

    @Version
    private Long version;

    @TableLogic(value = "0", delval = "-1")
    private Integer deleted;
}
