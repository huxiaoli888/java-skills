package com.chaken.ai.test.cms.auth.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.time.Instant;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@TableName("cms_admin_token")
public class AdminTokenEntity {
    @TableId(type = IdType.ASSIGN_ID)
    private Long id;
    private Long adminId;
    private String username;
    private String tokenHash;
    private String udid;
    private Integer status;
    private Instant expireTime;
    private Instant createTime;
    private Instant lastActiveTime;

    public boolean activeAt(Instant now) {
        return Integer.valueOf(1).equals(status) && expireTime != null && expireTime.isAfter(now);
    }
}
