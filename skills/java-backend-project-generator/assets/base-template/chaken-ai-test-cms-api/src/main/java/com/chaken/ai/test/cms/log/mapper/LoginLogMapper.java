package com.chaken.ai.test.cms.log.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.chaken.ai.test.cms.log.entity.LoginLogEntity;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface LoginLogMapper extends BaseMapper<LoginLogEntity> {
    Page<LoginLogEntity> selectLoginLogPage(
            Page<LoginLogEntity> page,
            @Param("keyword") String keyword,
            @Param("status") Integer status);
}
