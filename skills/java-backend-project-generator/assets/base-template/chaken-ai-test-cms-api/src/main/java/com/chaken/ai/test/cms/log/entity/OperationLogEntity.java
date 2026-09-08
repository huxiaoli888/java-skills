package com.chaken.ai.test.cms.log.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.time.Instant;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@TableName("cms_operation_log")
public class OperationLogEntity {
    @TableId(type = IdType.ASSIGN_ID)
    private Long id;

    private String operation;
    private String operationType;
    private String businessId;
    private String detail;
    private Boolean success;
    private String errorMessage;
    private String traceId;
    private String reqid;
    private String requestMethod;
    private String requestUri;
    private Long requestTime;
    private String userAgent;
    private String ip;
    private String creatorName;
    private Instant createTime;
}
