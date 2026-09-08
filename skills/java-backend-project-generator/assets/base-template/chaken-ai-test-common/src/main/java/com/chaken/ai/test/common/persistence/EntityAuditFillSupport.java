package com.chaken.ai.test.common.persistence;

import java.time.Instant;

public class EntityAuditFillSupport {
    private static final String SYSTEM_OPERATOR = "system";

    public void fillForInsert(BaseEntity entity) {
        Instant now = Instant.now();
        String operator = operator();
        if (entity.getCreateBy() == null || entity.getCreateBy().isBlank()) {
            entity.setCreateBy(operator);
        }
        if (entity.getCreateTime() == null) {
            entity.setCreateTime(now);
        }
        entity.setModifyBy(operator);
        entity.setModifyTime(now);
        if (entity.getVersion() == null) {
            entity.setVersion(0L);
        }
        if (entity.getDeleted() == null) {
            entity.setDeleted(LogicDeleteFlag.NORMAL);
        }
    }

    public void fillForUpdate(BaseEntity entity) {
        entity.setModifyBy(operator());
        entity.setModifyTime(Instant.now());
    }

    public void fillForLogicDelete(BaseEntity entity) {
        fillForUpdate(entity);
        entity.setDeleted(LogicDeleteFlag.DELETED);
    }

    private String operator() {
        String operator = OperatorContext.operatorId();
        return operator == null || operator.isBlank() ? SYSTEM_OPERATOR : operator;
    }
}
