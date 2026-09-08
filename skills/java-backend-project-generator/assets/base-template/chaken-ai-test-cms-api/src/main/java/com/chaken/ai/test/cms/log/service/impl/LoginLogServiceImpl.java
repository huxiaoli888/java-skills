package com.chaken.ai.test.cms.log.service.impl;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.chaken.ai.test.cms.log.dto.request.LoginLogPageQuery;
import com.chaken.ai.test.cms.log.dto.response.LoginLogResponse;
import com.chaken.ai.test.cms.log.entity.LoginLogEntity;
import com.chaken.ai.test.cms.log.mapper.LoginLogMapper;
import com.chaken.ai.test.cms.log.service.LoginLogService;
import com.chaken.ai.test.common.api.PageResult;
import java.time.Instant;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

@Service
public class LoginLogServiceImpl implements LoginLogService {
    private final LoginLogMapper mapper;

    public LoginLogServiceImpl(LoginLogMapper mapper) {
        this.mapper = mapper;
    }

    @Override
    public void save(LoginLogEntity entity) {
        if (entity.getCreateTime() == null) {
            entity.setCreateTime(Instant.now());
        }
        mapper.insert(entity);
    }

    @Override
    public PageResult<LoginLogResponse> page(LoginLogPageQuery query) {
        Page<LoginLogEntity> page = mapper.selectLoginLogPage(
                Page.of(query.getPage(), query.getPageSize()),
                normalize(query.getKeyword()),
                query.getStatus());
        return PageResult.of(
                page.getRecords().stream().map(LoginLogResponse::from).toList(),
                page.getTotal(),
                query.getPage(),
                query.getPageSize());
    }

    private String normalize(String value) {
        return StringUtils.hasText(value) ? value.trim() : null;
    }
}
