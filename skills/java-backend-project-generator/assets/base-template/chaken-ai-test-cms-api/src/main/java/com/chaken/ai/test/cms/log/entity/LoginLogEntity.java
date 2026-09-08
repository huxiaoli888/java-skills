package com.chaken.ai.test.cms.log.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.time.Instant;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@TableName("cms_login_log")
public class LoginLogEntity {
    @TableId(type = IdType.ASSIGN_ID)
    private Long id;

    private Integer operation;
    private Integer status;
    private String userAgent;
    private String ip;
    private String creatorName;
    private String traceId;
    private String reqid;
    private Instant createTime;
}
