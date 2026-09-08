package com.chaken.ai.test.cms.auth.service;

import com.chaken.ai.test.cms.auth.dto.request.CmsLoginRequest;
import com.chaken.ai.test.cms.auth.dto.response.CmsLoginResponse;
import com.chaken.ai.test.common.result.ServiceResult;
import jakarta.servlet.http.HttpServletRequest;

public interface CmsAuthService {
    ServiceResult<CmsLoginResponse> login(CmsLoginRequest request, HttpServletRequest httpRequest);

    void logout(String authorization, HttpServletRequest httpRequest);
}
