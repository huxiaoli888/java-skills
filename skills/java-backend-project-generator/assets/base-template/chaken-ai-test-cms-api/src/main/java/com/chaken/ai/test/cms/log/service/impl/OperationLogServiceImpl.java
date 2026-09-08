package com.chaken.ai.test.cms.log.service.impl;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.chaken.ai.test.cms.log.dto.request.OperationLogPageQuery;
import com.chaken.ai.test.cms.log.dto.response.OperationLogResponse;
import com.chaken.ai.test.cms.log.entity.OperationLogEntity;
import com.chaken.ai.test.cms.log.mapper.OperationLogMapper;
import com.chaken.ai.test.cms.log.service.OperationLogService;
import com.chaken.ai.test.common.api.PageResult;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

@Service
public class OperationLogServiceImpl implements OperationLogService {
    private final OperationLogMapper mapper;

    public OperationLogServiceImpl(OperationLogMapper mapper) {
        this.mapper = mapper;
    }

    @Override
    public PageResult<OperationLogResponse> page(OperationLogPageQuery query) {
        Page<OperationLogEntity> page = mapper.selectOperationLogPage(
                Page.of(query.getPage(), query.getPageSize()),
                normalize(query.getKeyword()),
                query.getSuccess());
        return PageResult.of(
                page.getRecords().stream().map(OperationLogResponse::from).toList(),
                page.getTotal(),
                query.getPage(),
                query.getPageSize());
    }

    private String normalize(String value) {
        return StringUtils.hasText(value) ? value.trim() : null;
    }
}
