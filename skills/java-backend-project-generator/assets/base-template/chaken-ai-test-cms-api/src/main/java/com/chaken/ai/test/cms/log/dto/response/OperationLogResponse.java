package com.chaken.ai.test.cms.log.dto.response;

import com.chaken.ai.test.cms.log.entity.OperationLogEntity;
import java.time.Instant;

public record OperationLogResponse(
        Long id,
        String operation,
        String operationType,
        String businessId,
        Boolean success,
        String errorMessage,
        String reqid,
        String traceId,
        String requestMethod,
        String requestUri,
        Long requestTime,
        String userAgent,
        String ip,
        String creatorName,
        Instant createTime) {
    public static OperationLogResponse from(OperationLogEntity entity) {
        return new OperationLogResponse(
                entity.getId(),
                entity.getOperation(),
                entity.getOperationType(),
                entity.getBusinessId(),
                entity.getSuccess(),
                entity.getErrorMessage(),
                entity.getReqid(),
                entity.getTraceId(),
                entity.getRequestMethod(),
                entity.getRequestUri(),
                entity.getRequestTime(),
                entity.getUserAgent(),
                entity.getIp(),
                entity.getCreatorName(),
                entity.getCreateTime());
    }
}
