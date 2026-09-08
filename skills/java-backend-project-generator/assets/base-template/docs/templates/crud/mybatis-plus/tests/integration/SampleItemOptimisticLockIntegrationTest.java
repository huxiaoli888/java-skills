package {{basePackage}}.cms.sampleitem;

import static org.assertj.core.api.Assertions.assertThat;

import {{basePackage}}.cms.sampleitem.entity.SampleItemEntity;
import {{basePackage}}.cms.sampleitem.mapper.SampleItemMapper;
import {{basePackage}}.common.persistence.EntityAuditFillSupport;
import {{basePackage}}.common.persistence.OperatorContext;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

@SpringBootTest
@ActiveProfiles("test")
class SampleItemOptimisticLockIntegrationTest {
    @Autowired
    private SampleItemMapper mapper;

    @Autowired
    private EntityAuditFillSupport auditFillSupport;

    @AfterEach
    void clearOperator() {
        OperatorContext.clear();
    }

    @Test
    void updateMustCarryCurrentVersion() {
        OperatorContext.put("tester");
        SampleItemEntity entity = new SampleItemEntity();
        entity.setName("version-item");
        auditFillSupport.fillForInsert(entity);
        mapper.insert(entity);

        SampleItemEntity update = mapper.selectById(entity.getId());
        update.setRemark("first update");
        update.setVersion(0L);
        auditFillSupport.fillForUpdate(update);

        int updated = mapper.updateById(update);

        assertThat(updated).isEqualTo(1);
        assertThat(mapper.selectById(entity.getId()).getVersion()).isEqualTo(1L);
    }
}
