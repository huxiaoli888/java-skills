package {{basePackage}}.cms.sampleitem.mapper;

import {{basePackage}}.cms.sampleitem.entity.SampleItemEntity;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface SampleItemMapper extends BaseMapper<SampleItemEntity> {
    List<SampleItemEntity> selectRecentActiveItems(@Param("keyword") String keyword, @Param("limit") int limit);
}
