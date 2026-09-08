package com.chaken.ai.test.cms.sys.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.chaken.ai.test.cms.sys.entity.SysRoleEntity;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface SysRoleMapper extends BaseMapper<SysRoleEntity> {
    List<SysRoleEntity> selectActiveRoles();
}
