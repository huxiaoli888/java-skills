package com.chaken.ai.test.cms.auth.service;

import com.chaken.ai.test.cms.auth.dto.response.CmsLoginResponse;
import com.chaken.ai.test.cms.security.AdminPrincipal;
import com.chaken.ai.test.cms.sys.entity.SysUserEntity;
import java.util.Optional;

public interface CmsTokenService {
    CmsLoginResponse issueToken(SysUserEntity user, String udid);

    Optional<AdminPrincipal> validateBearerToken(String authorization, String udid);

    void revokeBearerToken(String authorization);

    String tokenFingerprint(String authorization);
}
