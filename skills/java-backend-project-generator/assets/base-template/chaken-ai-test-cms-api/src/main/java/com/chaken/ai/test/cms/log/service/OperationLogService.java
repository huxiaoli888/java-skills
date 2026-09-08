package com.chaken.ai.test.cms.log.service;

import com.chaken.ai.test.cms.log.dto.request.OperationLogPageQuery;
import com.chaken.ai.test.cms.log.dto.response.OperationLogResponse;
import com.chaken.ai.test.common.api.PageResult;

public interface OperationLogService {
    PageResult<OperationLogResponse> page(OperationLogPageQuery query);
}
