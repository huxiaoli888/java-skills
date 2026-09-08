package com.chaken.ai.test.cms.auth.service.impl;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.isNull;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.chaken.ai.test.cms.auth.dto.request.CmsLoginRequest;
import com.chaken.ai.test.cms.auth.dto.response.CmsLoginResponse;
import com.chaken.ai.test.cms.auth.service.CmsTokenService;
import com.chaken.ai.test.cms.auth.service.PasswordHashService;
import com.chaken.ai.test.cms.log.entity.LoginLogEntity;
import com.chaken.ai.test.cms.log.service.LoginLogService;
import com.chaken.ai.test.cms.sys.entity.SysUserEntity;
import com.chaken.ai.test.cms.sys.mapper.SysUserMapper;
import java.time.Instant;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;

class CmsAuthServiceImplTest {

    @Test
    void loginDoesNotBindPublicRequestUdidToIssuedToken() {
        SysUserMapper userMapper = mock(SysUserMapper.class);
        PasswordHashService passwordHashService = mock(PasswordHashService.class);
        CmsTokenService tokenService = mock(CmsTokenService.class);
        LoginLogService loginLogService = mock(LoginLogService.class);
        CmsAuthServiceImpl service = new CmsAuthServiceImpl(
                userMapper,
                passwordHashService,
                tokenService,
                loginLogService);

        SysUserEntity user = new SysUserEntity();
        user.setId(1001L);
        user.setUsername("admin");
        user.setPasswordSalt("salt");
        user.setPasswordHash("hash");
        user.setStatus(1);
        when(userMapper.selectByUsername("admin")).thenReturn(user);
        when(passwordHashService.matches("secret", "salt", "hash")).thenReturn(true);
        when(tokenService.issueToken(any(SysUserEntity.class), isNull()))
                .thenReturn(new CmsLoginResponse("token", Instant.parse("2026-01-01T00:00:00Z"), "1001", "admin"));

        MockHttpServletRequest request = new MockHttpServletRequest();
        request.addHeader("x-udid", "login-device-should-not-bind");

        service.login(new CmsLoginRequest("admin", "secret"), request);

        verify(tokenService).issueToken(user, null);
        verify(loginLogService).save(any(LoginLogEntity.class));
    }
}
