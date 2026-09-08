package com.chaken.ai.test.cms.sys.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.chaken.ai.test.cms.sys.entity.SysUserEntity;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface SysUserMapper extends BaseMapper<SysUserEntity> {
    SysUserEntity selectByUsername(@Param("username") String username);

    Page<SysUserEntity> selectUserPage(
            Page<SysUserEntity> page,
            @Param("keyword") String keyword,
            @Param("status") Integer status);

    List<String> selectRoleCodes(@Param("userId") Long userId);

    List<String> selectPermissionCodes(@Param("userId") Long userId);
}
