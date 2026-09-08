package com.chaken.ai.test.cms.sys.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.chaken.ai.test.cms.sys.entity.SysMenuEntity;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface SysMenuMapper extends BaseMapper<SysMenuEntity> {
    List<SysMenuEntity> selectActiveMenus();

    List<SysMenuEntity> selectUserMenus(@Param("userId") Long userId);
}
