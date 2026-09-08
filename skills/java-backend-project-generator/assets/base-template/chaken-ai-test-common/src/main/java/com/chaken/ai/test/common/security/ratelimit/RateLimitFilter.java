package com.chaken.ai.test.common.security.ratelimit;

import com.chaken.ai.test.common.config.RateLimitProperties;
import com.chaken.ai.test.common.config.RateLimitProperties.RateLimitRule;
import com.chaken.ai.test.common.code.CommonErrorCode;
import com.chaken.ai.test.security.web.SecurityErrorResponseWriter;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import org.springframework.util.AntPathMatcher;
import org.springframework.web.filter.OncePerRequestFilter;

public class RateLimitFilter extends OncePerRequestFilter {
    private final RateLimitProperties properties;
    private final RateLimiter rateLimiter;
    private final AntPathMatcher pathMatcher = new AntPathMatcher();

    public RateLimitFilter(RateLimitProperties properties, RateLimiter rateLimiter) {
        this.properties = properties;
        this.rateLimiter = rateLimiter;
    }

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        return !properties.isEnabled() || matchesAny(properties.getExcludePaths(), pathWithinApplication(request));
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        String path = pathWithinApplication(request);
        RateLimitRule rule = matchRule(path);
        String key = "rate:" + request.getMethod() + ":" + path + ":" + resolveIdentity(request);
        if (!rateLimiter.tryAcquire(key, rule.getPermits(), rule.getWindow())) {
            SecurityErrorResponseWriter.write(response, CommonErrorCode.RATE_LIMITED);
            return;
        }
        filterChain.doFilter(request, response);
    }

    private RateLimitRule matchRule(String path) {
        for (RateLimitRule rule : properties.getRules()) {
            if (pathMatcher.match(rule.getPathPattern(), path)) {
                return rule;
            }
        }
        RateLimitRule fallback = new RateLimitRule();
        fallback.setPermits(properties.getDefaultPermits());
        fallback.setWindow(properties.getDefaultWindow());
        return fallback;
    }

    private String resolveIdentity(HttpServletRequest request) {
        for (String header : properties.getIdentityHeaders()) {
            String value = request.getHeader(header);
            if (value != null && !value.isBlank()) {
                return header + ":" + value;
            }
        }
        String forwardedFor = request.getHeader("x-forwarded-for");
        if (forwardedFor != null && !forwardedFor.isBlank()) {
            return "ip:" + forwardedFor.split(",", 2)[0].trim();
        }
        return "ip:" + request.getRemoteAddr();
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
