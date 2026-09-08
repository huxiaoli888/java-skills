package com.chaken.ai.test.cms.auth.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.chaken.ai.test.cms.auth.entity.AdminTokenEntity;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface AdminTokenMapper extends BaseMapper<AdminTokenEntity> {
    AdminTokenEntity selectActiveToken(@Param("tokenHash") String tokenHash);

    int revokeByTokenHash(@Param("tokenHash") String tokenHash);
}
