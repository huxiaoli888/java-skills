package com.chaken.ai.test.cms.sys.service.impl;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.chaken.ai.test.cms.sys.dto.request.SysParamPageQuery;
import com.chaken.ai.test.cms.sys.dto.response.SysParamResponse;
import com.chaken.ai.test.cms.sys.entity.SysParamEntity;
import com.chaken.ai.test.cms.sys.mapper.SysParamMapper;
import com.chaken.ai.test.cms.sys.service.SysParamService;
import com.chaken.ai.test.common.api.PageResult;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

@Service
public class SysParamServiceImpl implements SysParamService {
    private final SysParamMapper paramMapper;

    public SysParamServiceImpl(SysParamMapper paramMapper) {
        this.paramMapper = paramMapper;
    }

    @Override
    public PageResult<SysParamResponse> page(SysParamPageQuery query) {
        Page<SysParamEntity> page = paramMapper.selectParamPage(
                Page.of(query.getPage(), query.getPageSize()),
                normalize(query.getKeyword()),
                query.getStatus());
        return PageResult.of(
                page.getRecords().stream().map(SysParamResponse::from).toList(),
                page.getTotal(),
                query.getPage(),
                query.getPageSize());
    }

    private String normalize(String value) {
        return StringUtils.hasText(value) ? value.trim() : null;
    }
}
