package {{basePackage}}.cms.sampleitem;

import static org.assertj.core.api.Assertions.assertThat;

import {{basePackage}}.cms.sampleitem.entity.SampleItemEntity;
import {{basePackage}}.cms.sampleitem.mapper.SampleItemMapper;
import {{basePackage}}.common.persistence.EntityAuditFillSupport;
import {{basePackage}}.common.persistence.LogicDeleteFlag;
import {{basePackage}}.common.persistence.OperatorContext;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.ActiveProfiles;

@SpringBootTest
@ActiveProfiles("test")
class SampleItemLogicDeleteIntegrationTest {
    @Autowired
    private SampleItemMapper mapper;

    @Autowired
    private EntityAuditFillSupport auditFillSupport;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @AfterEach
    void clearOperator() {
        OperatorContext.clear();
    }

    @Test
    void logicDeleteMarksRecordDeletedInsteadOfRemovingIt() {
        OperatorContext.put("tester");
        SampleItemEntity entity = new SampleItemEntity();
        entity.setName("logic-delete-item");
        auditFillSupport.fillForInsert(entity);
        mapper.insert(entity);

        auditFillSupport.fillForLogicDelete(entity);
        mapper.update(null, new com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper<SampleItemEntity>()
                .eq(SampleItemEntity::getId, entity.getId())
                .eq(SampleItemEntity::getDeleted, LogicDeleteFlag.NORMAL)
                .set(SampleItemEntity::getDeleted, LogicDeleteFlag.DELETED)
                .set(SampleItemEntity::getModifyBy, entity.getModifyBy())
                .set(SampleItemEntity::getModifyTime, entity.getModifyTime()));

        assertThat(mapper.selectById(entity.getId())).isNull();
        Integer deleted = jdbcTemplate.queryForObject(
                "select deleted from sample_item where id = ?",
                Integer.class,
                entity.getId());
        assertThat(deleted).isEqualTo(LogicDeleteFlag.DELETED);
    }
}
