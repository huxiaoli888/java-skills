package com.chaken.ai.test.common.config;

import com.chaken.ai.test.common.security.sql.SqlInjectionFilter;
import com.chaken.ai.test.common.security.sql.SqlInjectionGuard;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
@EnableConfigurationProperties(SqlInjectionProperties.class)
public class SqlInjectionConfiguration {
    @Bean
    public SqlInjectionGuard sqlInjectionGuard(SqlInjectionProperties properties) {
        return new SqlInjectionGuard(properties.getBlockedPatterns());
    }

    @Bean
    public FilterRegistrationBean<SqlInjectionFilter> sqlInjectionFilterRegistration(
            SqlInjectionProperties properties,
            SqlInjectionGuard sqlInjectionGuard) {
        FilterRegistrationBean<SqlInjectionFilter> registration = new FilterRegistrationBean<>();
        registration.setFilter(new SqlInjectionFilter(properties, sqlInjectionGuard));
        registration.setOrder(Integer.MIN_VALUE + 5);
        registration.addUrlPatterns("/*");
        return registration;
    }
}
