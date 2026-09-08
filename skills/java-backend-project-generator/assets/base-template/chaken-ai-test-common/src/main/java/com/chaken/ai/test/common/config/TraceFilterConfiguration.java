package com.chaken.ai.test.common.config;

import com.chaken.ai.test.common.trace.RequestTraceLogFilter;
import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class TraceFilterConfiguration {
    @Bean
    public FilterRegistrationBean<RequestTraceLogFilter> requestTraceLogFilterRegistration() {
        FilterRegistrationBean<RequestTraceLogFilter> registration = new FilterRegistrationBean<>();
        registration.setFilter(new RequestTraceLogFilter());
        registration.setOrder(Integer.MIN_VALUE);
        registration.addUrlPatterns("/*");
        return registration;
    }
}
