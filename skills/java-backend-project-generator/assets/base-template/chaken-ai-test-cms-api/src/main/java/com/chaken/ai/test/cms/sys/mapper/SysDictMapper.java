package com.chaken.ai.test.cms.sys.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.chaken.ai.test.cms.sys.entity.SysDictEntity;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface SysDictMapper extends BaseMapper<SysDictEntity> {
    Page<SysDictEntity> selectDictPage(
            Page<SysDictEntity> page,
            @Param("keyword") String keyword,
            @Param("status") Integer status);
}
