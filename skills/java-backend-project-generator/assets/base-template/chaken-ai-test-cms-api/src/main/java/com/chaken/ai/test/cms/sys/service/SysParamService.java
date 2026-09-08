package com.chaken.ai.test.cms.sys.service;

import com.chaken.ai.test.cms.sys.dto.request.SysParamPageQuery;
import com.chaken.ai.test.cms.sys.dto.response.SysParamResponse;
import com.chaken.ai.test.common.api.PageResult;

public interface SysParamService {
    PageResult<SysParamResponse> page(SysParamPageQuery query);
}
