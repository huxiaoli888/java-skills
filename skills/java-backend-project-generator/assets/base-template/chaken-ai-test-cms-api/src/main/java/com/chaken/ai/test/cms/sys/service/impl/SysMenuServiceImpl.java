package com.chaken.ai.test.cms.sys.service.impl;

import com.chaken.ai.test.cms.sys.dto.response.SysMenuResponse;
import com.chaken.ai.test.cms.sys.mapper.SysMenuMapper;
import com.chaken.ai.test.cms.sys.service.SysMenuService;
import java.util.List;
import org.springframework.stereotype.Service;

@Service
public class SysMenuServiceImpl implements SysMenuService {
    private final SysMenuMapper menuMapper;

    public SysMenuServiceImpl(SysMenuMapper menuMapper) {
        this.menuMapper = menuMapper;
    }

    @Override
    public List<SysMenuResponse> listActiveMenus() {
        return menuMapper.selectActiveMenus().stream().map(SysMenuResponse::from).toList();
    }
}
