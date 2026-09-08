package com.chaken.ai.test.cms.sys.service;

import com.chaken.ai.test.cms.sys.dto.request.SysDictPageQuery;
import com.chaken.ai.test.cms.sys.dto.response.SysDictItemResponse;
import com.chaken.ai.test.cms.sys.dto.response.SysDictResponse;
import com.chaken.ai.test.common.api.PageResult;
import java.util.List;

public interface SysDictService {
    PageResult<SysDictResponse> page(SysDictPageQuery query);

    List<SysDictItemResponse> listItems(String dictCode);
}
