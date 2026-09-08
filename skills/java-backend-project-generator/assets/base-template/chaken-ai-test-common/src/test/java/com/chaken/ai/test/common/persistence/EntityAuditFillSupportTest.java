package com.chaken.ai.test.common.persistence;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;

class EntityAuditFillSupportTest {
    private final EntityAuditFillSupport fillSupport = new EntityAuditFillSupport();

    @AfterEach
    void tearDown() {
        OperatorContext.clear();
    }

    @Test
    void shouldFillInsertAuditFields() {
        OperatorContext.put("udid-001");
        DemoEntity entity = new DemoEntity();

        fillSupport.fillForInsert(entity);

        assertThat(entity.getId()).isNull();
        assertThat(entity.getCreateBy()).isEqualTo("udid-001");
        assertThat(entity.getCreateTime()).isNotNull();
        assertThat(entity.getModifyBy()).isEqualTo("udid-001");
        assertThat(entity.getModifyTime()).isNotNull();
        assertThat(entity.getVersion()).isZero();
        assertThat(entity.getDeleted()).isEqualTo(LogicDeleteFlag.NORMAL);
    }

    @Test
    void shouldMarkLogicDelete() {
        DemoEntity entity = new DemoEntity();
        fillSupport.fillForInsert(entity);

        fillSupport.fillForLogicDelete(entity);

        assertThat(entity.getDeleted()).isEqualTo(LogicDeleteFlag.DELETED);
        assertThat(entity.getModifyTime()).isNotNull();
    }

    private static final class DemoEntity extends BaseEntity {
    }
}
