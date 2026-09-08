package com.chaken.ai.test.cms.sys.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.chaken.ai.test.cms.sys.entity.SysParamEntity;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface SysParamMapper extends BaseMapper<SysParamEntity> {
    Page<SysParamEntity> selectParamPage(
            Page<SysParamEntity> page,
            @Param("keyword") String keyword,
            @Param("status") Integer status);
}
