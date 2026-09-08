package com.chaken.ai.test.cms.sys.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.chaken.ai.test.cms.sys.entity.SysDictItemEntity;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface SysDictItemMapper extends BaseMapper<SysDictItemEntity> {
    List<SysDictItemEntity> selectActiveItems(@Param("dictCode") String dictCode);
}
