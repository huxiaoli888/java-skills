package com.chaken.ai.test.sdk.security;

import com.chaken.ai.test.common.code.CommonErrorCode;
import com.chaken.ai.test.security.credential.ApiCredentialResolver;
import com.chaken.ai.test.security.replay.ReplayRequestStore;
import com.chaken.ai.test.security.signature.AuthenticatedSignatureRequest;
import com.chaken.ai.test.security.signature.SignatureAuthenticationException;
import com.chaken.ai.test.security.signature.SignatureAuthenticationSupport;
import com.chaken.ai.test.security.signature.SignatureHeaders;
import com.chaken.ai.test.security.web.SecurityErrorResponseWriter;
import com.chaken.ai.test.sdk.security.config.SdkSecurityProperties;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.util.AntPathMatcher;
import org.springframework.web.filter.OncePerRequestFilter;

public class SdkSecurityFilter extends OncePerRequestFilter {
    public static final String REQUEST_FINGERPRINT_ATTRIBUTE =
            SignatureAuthenticationSupport.REQUEST_FINGERPRINT_ATTRIBUTE;
    private static final Logger log = LoggerFactory.getLogger(SdkSecurityFilter.class);
    private static final String SDK_PATH_PREFIX = "/api/v1/sdk/";

    private final SdkSecurityProperties properties;
    private final SignatureAuthenticationSupport signatureAuthenticationSupport;
    private final AntPathMatcher pathMatcher = new AntPathMatcher();

    public SdkSecurityFilter(
            SdkSecurityProperties properties,
            ApiCredentialResolver apiCredentialResolver,
            ReplayRequestStore replayRequestStore) {
        this.properties = properties;
        this.signatureAuthenticationSupport = new SignatureAuthenticationSupport(apiCredentialResolver, replayRequestStore);
    }

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        return !properties.isSignatureEnabled()
                || !pathWithinApplication(request).startsWith(SDK_PATH_PREFIX);
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        if (isAuthExcluded(request)) {
            filterChain.doFilter(request, response);
            return;
        }

        if (!isUdidExcluded(request) && isBlank(request.getHeader(SignatureHeaders.UDID))) {
            SecurityErrorResponseWriter.write(response, CommonErrorCode.PARAM_INVALID);
            return;
        }

        try {
            AuthenticatedSignatureRequest authenticated =
                    signatureAuthenticationSupport.authenticate(request, properties.getReplayWindow());
            filterChain.doFilter(authenticated.request(), response);
        } catch (SignatureAuthenticationException ex) {
            log.info("sdk_signature_auth_failed path={} code={}",
                    pathWithinApplication(request), ex.errorCode().code());
            SecurityErrorResponseWriter.write(response, ex.errorCode());
        }
    }

    private boolean isAuthExcluded(HttpServletRequest request) {
        return matchesAny(properties.getAuthExcludePaths(), pathWithinApplication(request));
    }

    private boolean isUdidExcluded(HttpServletRequest request) {
        return matchesAny(properties.getUdidExcludePaths(), pathWithinApplication(request));
    }

    private boolean matchesAny(Iterable<String> patterns, String path) {
        for (String pattern : patterns) {
            if (pathMatcher.match(pattern, path)) {
                return true;
            }
        }
        return false;
    }

    private String pathWithinApplication(HttpServletRequest request) {
        String contextPath = request.getContextPath();
        String requestUri = request.getRequestURI();
        if (contextPath == null || contextPath.isEmpty()) {
            return requestUri;
        }
        return requestUri.startsWith(contextPath) ? requestUri.substring(contextPath.length()) : requestUri;
    }

    private boolean isBlank(String value) {
        return value == null || value.trim().isEmpty();
    }
}
