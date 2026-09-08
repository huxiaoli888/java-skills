package com.chaken.ai.test.cms.log.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.chaken.ai.test.cms.log.entity.OperationLogEntity;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface OperationLogMapper extends BaseMapper<OperationLogEntity> {
    Page<OperationLogEntity> selectOperationLogPage(
            Page<OperationLogEntity> page,
            @Param("keyword") String keyword,
            @Param("success") Boolean success);
}
