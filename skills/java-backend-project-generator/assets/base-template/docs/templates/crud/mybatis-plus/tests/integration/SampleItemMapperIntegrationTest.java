package {{basePackage}}.cms.sampleitem;

import static org.assertj.core.api.Assertions.assertThat;

import {{basePackage}}.cms.sampleitem.entity.SampleItemEntity;
import {{basePackage}}.cms.sampleitem.mapper.SampleItemMapper;
import {{basePackage}}.common.persistence.EntityAuditFillSupport;
import {{basePackage}}.common.persistence.LogicDeleteFlag;
import {{basePackage}}.common.persistence.OperatorContext;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import java.util.List;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

@SpringBootTest
@ActiveProfiles("test")
class SampleItemMapperIntegrationTest {
    @Autowired
    private SampleItemMapper mapper;

    @Autowired
    private EntityAuditFillSupport auditFillSupport;

    @AfterEach
    void clearOperator() {
        OperatorContext.clear();
    }

    @Test
    void insertAndQueryNormalRecord() {
        OperatorContext.put("tester");
        SampleItemEntity entity = new SampleItemEntity();
        entity.setName("integration-item");
        entity.setRemark("created by H2 integration test");
        auditFillSupport.fillForInsert(entity);

        int inserted = mapper.insert(entity);

        assertThat(inserted).isEqualTo(1);
        SampleItemEntity saved = mapper.selectOne(new LambdaQueryWrapper<SampleItemEntity>()
                .eq(SampleItemEntity::getName, "integration-item")
                .eq(SampleItemEntity::getDeleted, LogicDeleteFlag.NORMAL));
        assertThat(saved).isNotNull();
        assertThat(saved.getCreateBy()).isEqualTo("tester");
        assertThat(saved.getVersion()).isZero();

        List<SampleItemEntity> recentItems = mapper.selectRecentActiveItems("integration", 10);
        assertThat(recentItems).extracting(SampleItemEntity::getName).contains("integration-item");
    }
}
