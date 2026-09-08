package com.chaken.ai.test.cms.sys.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.time.Instant;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@TableName("cms_sys_param")
public class SysParamEntity {
    @TableId(type = IdType.ASSIGN_ID)
    private Long id;
    private String paramKey;
    private String paramValue;
    private String paramName;
    private Integer status;
    private String remark;
    private Instant createTime;
    private Instant modifyTime;
}
