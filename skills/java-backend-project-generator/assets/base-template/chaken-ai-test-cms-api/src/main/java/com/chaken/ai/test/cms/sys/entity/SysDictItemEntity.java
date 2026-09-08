package com.chaken.ai.test.cms.sys.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.time.Instant;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@TableName("cms_sys_dict_item")
public class SysDictItemEntity {
    @TableId(type = IdType.ASSIGN_ID)
    private Long id;
    private String dictCode;
    private String itemValue;
    private String itemLabel;
    private Integer sortNo;
    private Integer status;
    private String remark;
    private Instant createTime;
    private Instant modifyTime;
}
