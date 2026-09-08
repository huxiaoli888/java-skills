package com.chaken.ai.test.cms.sys.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.time.Instant;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@TableName("cms_sys_menu")
public class SysMenuEntity {
    @TableId(type = IdType.ASSIGN_ID)
    private Long id;
    private Long parentId;
    private String menuName;
    private String menuType;
    private String path;
    private String permissionCode;
    private Integer sortNo;
    private Integer status;
    private Instant createTime;
    private Instant modifyTime;
}
