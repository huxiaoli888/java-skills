package com.chaken.ai.test.cms.sys.service.impl;

import com.chaken.ai.test.cms.sys.dto.response.SysRoleResponse;
import com.chaken.ai.test.cms.sys.mapper.SysRoleMapper;
import com.chaken.ai.test.cms.sys.service.SysRoleService;
import java.util.List;
import org.springframework.stereotype.Service;

@Service
public class SysRoleServiceImpl implements SysRoleService {
    private final SysRoleMapper roleMapper;

    public SysRoleServiceImpl(SysRoleMapper roleMapper) {
        this.roleMapper = roleMapper;
    }

    @Override
    public List<SysRoleResponse> listActiveRoles() {
        return roleMapper.selectActiveRoles().stream().map(SysRoleResponse::from).toList();
    }
}
