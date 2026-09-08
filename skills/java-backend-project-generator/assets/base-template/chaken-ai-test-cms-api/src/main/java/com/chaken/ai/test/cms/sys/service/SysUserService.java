package com.chaken.ai.test.cms.sys.service;

import com.chaken.ai.test.cms.sys.dto.request.SysUserPageQuery;
import com.chaken.ai.test.cms.sys.dto.response.SysCurrentUserResponse;
import com.chaken.ai.test.cms.sys.dto.response.SysUserResponse;
import com.chaken.ai.test.common.api.PageResult;

public interface SysUserService {
    PageResult<SysUserResponse> page(SysUserPageQuery query);

    SysCurrentUserResponse currentUser();
}
