package com.chaken.ai.test.cms.sys.service.impl;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.chaken.ai.test.cms.sys.dto.request.SysUserPageQuery;
import com.chaken.ai.test.cms.sys.dto.response.SysCurrentUserResponse;
import com.chaken.ai.test.cms.sys.dto.response.SysMenuResponse;
import com.chaken.ai.test.cms.sys.dto.response.SysUserResponse;
import com.chaken.ai.test.cms.sys.entity.SysMenuEntity;
import com.chaken.ai.test.cms.sys.entity.SysUserEntity;
import com.chaken.ai.test.cms.sys.mapper.SysMenuMapper;
import com.chaken.ai.test.cms.sys.mapper.SysUserMapper;
import com.chaken.ai.test.cms.sys.service.SysUserService;
import com.chaken.ai.test.common.api.PageResult;
import com.chaken.ai.test.common.permission.model.AuthenticatedPrincipal;
import com.chaken.ai.test.common.permission.context.PrincipalContext;
import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

@Service
public class SysUserServiceImpl implements SysUserService {
    private final SysUserMapper userMapper;
    private final SysMenuMapper menuMapper;

    public SysUserServiceImpl(SysUserMapper userMapper, SysMenuMapper menuMapper) {
        this.userMapper = userMapper;
        this.menuMapper = menuMapper;
    }

    @Override
    public PageResult<SysUserResponse> page(SysUserPageQuery query) {
        Page<SysUserEntity> page = userMapper.selectUserPage(
                Page.of(query.getPage(), query.getPageSize()),
                normalize(query.getKeyword()),
                query.getStatus());
        return PageResult.of(
                page.getRecords().stream().map(SysUserResponse::from).toList(),
                page.getTotal(),
                query.getPage(),
                query.getPageSize());
    }

    @Override
    public SysCurrentUserResponse currentUser() {
        AuthenticatedPrincipal principal = PrincipalContext.current().orElseThrow();
        Long userId = Long.valueOf(principal.principalId());
        SysUserEntity user = userMapper.selectById(userId);
        List<SysMenuResponse> menus = menuMapper.selectUserMenus(userId).stream()
                .map(SysMenuResponse::from)
                .toList();
        return new SysCurrentUserResponse(
                principal.principalId(),
                user == null ? "" : user.getUsername(),
                user == null ? "" : user.getDisplayName(),
                user != null && Boolean.TRUE.equals(user.getSuperAdmin()),
                principal.roles().stream().sorted().toList(),
                principal.permissions().stream().sorted().toList(),
                menus);
    }

    private String normalize(String value) {
        return StringUtils.hasText(value) ? value.trim() : null;
    }
}
