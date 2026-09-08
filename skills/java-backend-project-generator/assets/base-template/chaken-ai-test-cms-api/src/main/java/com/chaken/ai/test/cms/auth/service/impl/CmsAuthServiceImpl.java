package com.chaken.ai.test.cms.auth.service.impl;

import com.chaken.ai.test.cms.auth.dto.request.CmsLoginRequest;
import com.chaken.ai.test.cms.auth.dto.response.CmsLoginResponse;
import com.chaken.ai.test.cms.auth.service.CmsAuthService;
import com.chaken.ai.test.cms.auth.service.CmsTokenService;
import com.chaken.ai.test.cms.auth.service.PasswordHashService;
import com.chaken.ai.test.cms.log.entity.LoginLogEntity;
import com.chaken.ai.test.cms.log.service.LoginLogService;
import com.chaken.ai.test.cms.security.AdminPrincipal;
import com.chaken.ai.test.cms.security.CmsSecurityFilter;
import com.chaken.ai.test.cms.sys.entity.SysUserEntity;
import com.chaken.ai.test.cms.sys.mapper.SysUserMapper;
import com.chaken.ai.test.common.code.CommonErrorCode;
import com.chaken.ai.test.common.result.ServiceResult;
import com.chaken.ai.test.common.trace.TraceContext;
import jakarta.servlet.http.HttpServletRequest;
import java.time.Instant;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class CmsAuthServiceImpl implements CmsAuthService {
    private static final int OPERATION_LOGIN = 0;
    private static final int OPERATION_LOGOUT = 1;
    private static final int STATUS_FAILED = 0;
    private static final int STATUS_SUCCESS = 1;

    private final SysUserMapper userMapper;
    private final PasswordHashService passwordHashService;
    private final CmsTokenService tokenService;
    private final LoginLogService loginLogService;

    public CmsAuthServiceImpl(
            SysUserMapper userMapper,
            PasswordHashService passwordHashService,
            CmsTokenService tokenService,
            LoginLogService loginLogService) {
        this.userMapper = userMapper;
        this.passwordHashService = passwordHashService;
        this.tokenService = tokenService;
        this.loginLogService = loginLogService;
    }

    @Override
    @Transactional
    public ServiceResult<CmsLoginResponse> login(CmsLoginRequest request, HttpServletRequest httpRequest) {
        SysUserEntity user = userMapper.selectByUsername(request.username());
        if (user == null || !user.active()
                || !passwordHashService.matches(request.password(), user.getPasswordSalt(), user.getPasswordHash())) {
            saveLoginLog(OPERATION_LOGIN, STATUS_FAILED, request.username(), httpRequest);
            return ServiceResult.failure(CommonErrorCode.UNAUTHORIZED);
        }
        CmsLoginResponse response = tokenService.issueToken(user, null);
        saveLoginLog(OPERATION_LOGIN, STATUS_SUCCESS, user.getUsername(), httpRequest);
        return ServiceResult.success(response);
    }

    @Override
    @Transactional
    public void logout(String authorization, HttpServletRequest httpRequest) {
        tokenService.revokeBearerToken(authorization);
        Object principal = httpRequest.getAttribute(CmsSecurityFilter.ADMIN_PRINCIPAL_ATTRIBUTE);
        String username = principal instanceof AdminPrincipal adminPrincipal
                ? adminPrincipal.username()
                : String.valueOf(httpRequest.getAttribute("adminId"));
        saveLoginLog(OPERATION_LOGOUT, STATUS_SUCCESS, username, httpRequest);
    }

    private void saveLoginLog(int operation, int status, String username, HttpServletRequest request) {
        LoginLogEntity entity = new LoginLogEntity();
        entity.setOperation(operation);
        entity.setStatus(status);
        entity.setCreatorName(username);
        entity.setTraceId(TraceContext.traceId());
        entity.setReqid(TraceContext.requestId());
        entity.setIp(clientIp(request));
        entity.setUserAgent(request.getHeader("user-agent"));
        entity.setCreateTime(Instant.now());
        loginLogService.save(entity);
    }

    private String clientIp(HttpServletRequest request) {
        String forwarded = request.getHeader("x-forwarded-for");
        if (forwarded != null && !forwarded.isBlank()) {
            return forwarded.split(",")[0].trim();
        }
        return request.getRemoteAddr();
    }
}
