package com.chaken.ai.test.cms.sys.service.impl;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.chaken.ai.test.cms.sys.dto.request.SysDictPageQuery;
import com.chaken.ai.test.cms.sys.dto.response.SysDictItemResponse;
import com.chaken.ai.test.cms.sys.dto.response.SysDictResponse;
import com.chaken.ai.test.cms.sys.entity.SysDictEntity;
import com.chaken.ai.test.cms.sys.mapper.SysDictItemMapper;
import com.chaken.ai.test.cms.sys.mapper.SysDictMapper;
import com.chaken.ai.test.cms.sys.service.SysDictService;
import com.chaken.ai.test.common.api.PageResult;
import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

@Service
public class SysDictServiceImpl implements SysDictService {
    private final SysDictMapper dictMapper;
    private final SysDictItemMapper dictItemMapper;

    public SysDictServiceImpl(SysDictMapper dictMapper, SysDictItemMapper dictItemMapper) {
        this.dictMapper = dictMapper;
        this.dictItemMapper = dictItemMapper;
    }

    @Override
    public PageResult<SysDictResponse> page(SysDictPageQuery query) {
        Page<SysDictEntity> page = dictMapper.selectDictPage(
                Page.of(query.getPage(), query.getPageSize()),
                normalize(query.getKeyword()),
                query.getStatus());
        return PageResult.of(
                page.getRecords().stream().map(SysDictResponse::from).toList(),
                page.getTotal(),
                query.getPage(),
                query.getPageSize());
    }

    @Override
    public List<SysDictItemResponse> listItems(String dictCode) {
        return dictItemMapper.selectActiveItems(dictCode).stream()
                .map(SysDictItemResponse::from)
                .toList();
    }

    private String normalize(String value) {
        return StringUtils.hasText(value) ? value.trim() : null;
    }
}
