package com.chaken.ai.test.cms.security;

import com.chaken.ai.test.cms.auth.service.CmsTokenService;
import com.chaken.ai.test.common.permission.model.AuthenticatedPrincipal;
import com.chaken.ai.test.common.permission.context.DataPermissionContext;
import com.chaken.ai.test.common.permission.model.DataPermissionScope;
import com.chaken.ai.test.common.permission.context.PrincipalContext;
import com.chaken.ai.test.common.permission.context.TenantContext;
import com.chaken.ai.test.common.code.CommonErrorCode;
import com.chaken.ai.test.security.body.CachedBodyHttpServletRequest;
import com.chaken.ai.test.security.replay.ReplayRequestStore;
import com.chaken.ai.test.security.signature.SignatureCanonicalPayload;
import com.chaken.ai.test.security.signature.RequestSigner;
import com.chaken.ai.test.security.signature.SignatureHeaders;
import com.chaken.ai.test.security.web.SecurityErrorResponseWriter;
import com.chaken.ai.test.common.trace.TraceContext;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.time.Instant;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.util.AntPathMatcher;
import org.springframework.util.StreamUtils;
import org.springframework.web.filter.OncePerRequestFilter;

public class CmsSecurityFilter extends OncePerRequestFilter {
    public static final String ADMIN_PRINCIPAL_ATTRIBUTE = AdminPrincipal.class.getName();
    private static final Logger log = LoggerFactory.getLogger(CmsSecurityFilter.class);
    private static final String CMS_PATH_PREFIX = "/api/v1/cms/";
    private static final String BEARER_PREFIX = "Bearer ";
    private static final String SIGNATURE_ALG = "HMAC-SHA256";

    private final CmsSecurityProperties properties;
    private final ReplayRequestStore replayRequestStore;
    private final CmsTokenService tokenService;
    private final AntPathMatcher pathMatcher = new AntPathMatcher();

    public CmsSecurityFilter(
            CmsSecurityProperties properties,
            ReplayRequestStore replayRequestStore,
            CmsTokenService tokenService) {
        this.properties = properties;
        this.replayRequestStore = replayRequestStore;
        this.tokenService = tokenService;
    }

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        return !properties.isEnabled()
                || !pathWithinApplication(request).startsWith(CMS_PATH_PREFIX);
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        if (isAuthExcluded(request)) {
            filterChain.doFilter(request, response);
            return;
        }

        String authorization = request.getHeader(SignatureHeaders.AUTHORIZATION);
        String udid = request.getHeader(SignatureHeaders.UDID);
        if (!isUdidExcluded(request) && isBlank(udid)) {
            SecurityErrorResponseWriter.write(response, CommonErrorCode.PARAM_INVALID);
            return;
        }

        Optional<AdminPrincipal> principal = tokenService.validateBearerToken(authorization, udid);
        if (principal.isEmpty()) {
            SecurityErrorResponseWriter.write(response, CommonErrorCode.UNAUTHORIZED);
            return;
        }

        HttpServletRequest authenticatedRequest = request;
        if (properties.isSignatureEnabled()) {
            SignatureCheckResult result = verifySignature(request, authorization, udid);
            if (!result.valid()) {
                SecurityErrorResponseWriter.write(response, result.errorCode());
                return;
            }
            authenticatedRequest = result.request();
        }

        AdminPrincipal adminPrincipal = principal.get();
        authenticatedRequest.setAttribute("adminId", adminPrincipal.adminId());
        authenticatedRequest.setAttribute(ADMIN_PRINCIPAL_ATTRIBUTE, adminPrincipal);
        PrincipalContext.put(new AuthenticatedPrincipal(
                adminPrincipal.adminId(),
                udid,
                "",
                adminPrincipal.permissions(),
                adminPrincipal.roles()));
        TenantContext.put("");
        DataPermissionContext.put(DataPermissionScope.allForTenant(""));
        try {
            filterChain.doFilter(authenticatedRequest, response);
        } finally {
            DataPermissionContext.clear();
            TenantContext.clear();
            PrincipalContext.clear();
        }
    }

    private SignatureCheckResult verifySignature(HttpServletRequest request, String authorization, String udid)
            throws IOException {
        String timestamp = request.getHeader(SignatureHeaders.TIMESTAMP);
        String reqid = request.getHeader(SignatureHeaders.REQID);
        String signatureAlg = request.getHeader(SignatureHeaders.SIGNATURE_ALG);
        String apiVersion = request.getHeader(SignatureHeaders.API_VERSION);
        String signature = request.getHeader(SignatureHeaders.SIGN);
        if (isBlank(timestamp) || isBlank(reqid) || isBlank(signatureAlg) || isBlank(apiVersion) || isBlank(signature)) {
            return SignatureCheckResult.error(CommonErrorCode.PARAM_INVALID);
        }
        if (!SIGNATURE_ALG.equalsIgnoreCase(signatureAlg)) {
            return SignatureCheckResult.error(CommonErrorCode.SIGNATURE_INVALID);
        }
        if (isExpired(timestamp, reqid)) {
            return SignatureCheckResult.error(CommonErrorCode.REQUEST_EXPIRED);
        }

        CachedBodyHttpServletRequest wrappedRequest = cachedRequest(request);
        byte[] canonicalBody = SignatureCanonicalPayload.body(request, wrappedRequest.getCachedBody());
        byte[] canonicalBytes = cmsCanonicalBytes(
                request.getMethod(),
                request.getRequestURI(),
                SignatureCanonicalPayload.query(request),
                timestamp,
                reqid,
                authorization,
                udid,
                signatureAlg,
                apiVersion,
                canonicalBody);
        String expectedSignature = RequestSigner.hmacSha256Base64(properties.getDefaultSignSecret(), canonicalBytes);
        if (!RequestSigner.constantTimeEquals(expectedSignature, signature)) {
            return SignatureCheckResult.error(CommonErrorCode.SIGNATURE_INVALID);
        }
        if (!replayRequestStore.saveIfAbsent(cmsReplaySubject(authorization, udid), reqid, properties.getReplayWindow())) {
            return SignatureCheckResult.error(CommonErrorCode.REPLAY_REQUEST);
        }
        return SignatureCheckResult.ok(wrappedRequest);
    }

    private String cmsReplaySubject(String authorization, String udid) {
        return tokenService.tokenFingerprint(authorization) + ":" + udid;
    }

    private byte[] cmsCanonicalBytes(
            String method,
            String path,
            String query,
            String timestamp,
            String reqid,
            String authorization,
            String udid,
            String signatureAlg,
            String apiVersion,
            byte[] rawBody) {
        String prefix = String.join("\n",
                method == null ? "" : method.toUpperCase(),
                path == null ? "" : path,
                query == null ? "" : query,
                timestamp,
                reqid,
                authorization,
                udid,
                signatureAlg,
                apiVersion) + "\n";
        byte[] prefixBytes = prefix.getBytes(java.nio.charset.StandardCharsets.UTF_8);
        byte[] body = rawBody == null ? new byte[0] : rawBody;
        byte[] result = java.util.Arrays.copyOf(prefixBytes, prefixBytes.length + body.length);
        System.arraycopy(body, 0, result, prefixBytes.length, body.length);
        return result;
    }

    private CachedBodyHttpServletRequest cachedRequest(HttpServletRequest request) throws IOException {
        if (request instanceof CachedBodyHttpServletRequest cachedRequest) {
            return cachedRequest;
        }
        return new CachedBodyHttpServletRequest(request, StreamUtils.copyToByteArray(request.getInputStream()));
    }

    private boolean isExpired(String timestamp, String reqid) {
        try {
            Instant requestTime = timestamp.matches("\\d+")
                    ? Instant.ofEpochMilli(Long.parseLong(timestamp))
                    : Instant.parse(timestamp);
            Instant now = Instant.now();
            return requestTime.isBefore(now.minus(properties.getReplayWindow()))
                    || requestTime.isAfter(now.plus(properties.getReplayWindow()));
        } catch (RuntimeException ex) {
            log.info("cms_signature_timestamp_invalid reqid={}", firstNonBlank(reqid, TraceContext.requestId()));
            return true;
        }
    }

    private String firstNonBlank(String first, String second) {
        return isBlank(first) ? second : first;
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

    private record SignatureCheckResult(
            boolean valid,
            HttpServletRequest request,
            CommonErrorCode errorCode) {
        static SignatureCheckResult ok(HttpServletRequest request) {
            return new SignatureCheckResult(true, request, CommonErrorCode.SUCCESS);
        }

        static SignatureCheckResult error(CommonErrorCode errorCode) {
            return new SignatureCheckResult(false, null, errorCode);
        }
    }
}
