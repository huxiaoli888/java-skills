package com.chaken.ai.test.common.security.sql;

import com.chaken.ai.test.common.config.SqlInjectionProperties;
import com.chaken.ai.test.common.code.CommonErrorCode;
import com.chaken.ai.test.security.web.SecurityErrorResponseWriter;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.Map;
import org.springframework.util.AntPathMatcher;
import org.springframework.web.filter.OncePerRequestFilter;

public class SqlInjectionFilter extends OncePerRequestFilter {
    private static final String FORM_CONTENT_TYPE = "application/x-www-form-urlencoded";

    private final SqlInjectionProperties properties;
    private final SqlInjectionGuard sqlInjectionGuard;
    private final AntPathMatcher pathMatcher = new AntPathMatcher();

    public SqlInjectionFilter(SqlInjectionProperties properties, SqlInjectionGuard sqlInjectionGuard) {
        this.properties = properties;
        this.sqlInjectionGuard = sqlInjectionGuard;
    }

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        return !properties.isEnabled() || matchesAny(properties.getExcludePaths(), pathWithinApplication(request));
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        if (hasRisk(request)) {
            SecurityErrorResponseWriter.write(response, CommonErrorCode.PARAM_INVALID);
            return;
        }
        filterChain.doFilter(request, response);
    }

    private boolean hasRisk(HttpServletRequest request) {
        if (properties.isCheckQueryParameters() && sqlInjectionGuard.hasInjectionRisk(request.getQueryString())) {
            return true;
        }
        if (properties.isCheckFormParameters() && isFormRequest(request)) {
            return hasRisk(request.getParameterMap());
        }
        return false;
    }

    private boolean hasRisk(Map<String, String[]> parameters) {
        for (Map.Entry<String, String[]> entry : parameters.entrySet()) {
            if (sqlInjectionGuard.hasInjectionRisk(entry.getKey())) {
                return true;
            }
            for (String value : entry.getValue()) {
                if (sqlInjectionGuard.hasInjectionRisk(value)) {
                    return true;
                }
            }
        }
        return false;
    }

    private boolean isFormRequest(HttpServletRequest request) {
        String contentType = request.getContentType();
        return contentType != null && contentType.toLowerCase().startsWith(FORM_CONTENT_TYPE);
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
}
