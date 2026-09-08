package com.chaken.ai.test.cms.sys.service;

import com.chaken.ai.test.cms.sys.dto.response.SysRoleResponse;
import java.util.List;

public interface SysRoleService {
    List<SysRoleResponse> listActiveRoles();
}
