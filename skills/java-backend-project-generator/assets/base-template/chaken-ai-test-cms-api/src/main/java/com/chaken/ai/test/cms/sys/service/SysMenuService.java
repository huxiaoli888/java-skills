package com.chaken.ai.test.cms.sys.service;

import com.chaken.ai.test.cms.sys.dto.response.SysMenuResponse;
import java.util.List;

public interface SysMenuService {
    List<SysMenuResponse> listActiveMenus();
}
