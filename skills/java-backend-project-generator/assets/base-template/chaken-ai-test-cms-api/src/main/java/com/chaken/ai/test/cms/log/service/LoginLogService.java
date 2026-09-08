package com.chaken.ai.test.cms.log.service;

import com.chaken.ai.test.cms.log.dto.request.LoginLogPageQuery;
import com.chaken.ai.test.cms.log.dto.response.LoginLogResponse;
import com.chaken.ai.test.cms.log.entity.LoginLogEntity;
import com.chaken.ai.test.common.api.PageResult;

public interface LoginLogService {
    void save(LoginLogEntity entity);

    PageResult<LoginLogResponse> page(LoginLogPageQuery query);
}
