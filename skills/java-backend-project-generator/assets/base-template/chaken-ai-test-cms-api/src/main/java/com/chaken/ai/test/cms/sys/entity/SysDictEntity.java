package com.chaken.ai.test.cms.sys.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.time.Instant;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@TableName("cms_sys_dict")
public class SysDictEntity {
    @TableId(type = IdType.ASSIGN_ID)
    private Long id;
    private String dictCode;
    private String dictName;
    private Integer status;
    private String remark;
    private Instant createTime;
    private Instant modifyTime;
}
