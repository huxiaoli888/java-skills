package com.chaken.ai.test.cms.log.dto.response;

import com.chaken.ai.test.cms.log.entity.LoginLogEntity;
import java.time.Instant;

public record LoginLogResponse(
        Long id,
        Integer operation,
        Integer status,
        String userAgent,
        String ip,
        String creatorName,
        String reqid,
        String traceId,
        Instant createTime) {
    public static LoginLogResponse from(LoginLogEntity entity) {
        return new LoginLogResponse(
                entity.getId(),
                entity.getOperation(),
                entity.getStatus(),
                entity.getUserAgent(),
                entity.getIp(),
                entity.getCreatorName(),
                entity.getReqid(),
                entity.getTraceId(),
                entity.getCreateTime());
    }
}
