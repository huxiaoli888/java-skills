package com.chaken.ai.test.cms.sys.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.time.Instant;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@TableName("cms_sys_user")
public class SysUserEntity {
    @TableId(type = IdType.ASSIGN_ID)
    private Long id;
    private String username;
    private String displayName;
    private String mobile;
    private String email;
    private String passwordSalt;
    private String passwordHash;
    private Integer status;
    private Boolean superAdmin;
    private Instant createTime;
    private Instant modifyTime;

    public boolean active() {
        return Integer.valueOf(1).equals(status);
    }
}
