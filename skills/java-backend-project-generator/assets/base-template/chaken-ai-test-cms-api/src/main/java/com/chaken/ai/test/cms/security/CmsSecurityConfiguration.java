package com.chaken.ai.test.cms.security;

import com.chaken.ai.test.cms.auth.service.CmsTokenService;
import com.chaken.ai.test.security.replay.InMemoryReplayRequestStore;
import com.chaken.ai.test.security.replay.ReplayRequestStore;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
@EnableConfigurationProperties(CmsSecurityProperties.class)
public class CmsSecurityConfiguration {
    @Bean
    public ReplayRequestStore cmsReplayRequestStore() {
        return new InMemoryReplayRequestStore();
    }

    @Bean
    public FilterRegistrationBean<CmsSecurityFilter> cmsSecurityFilterRegistration(
            CmsSecurityProperties properties,
            ReplayRequestStore cmsReplayRequestStore,
            CmsTokenService cmsTokenService) {
        FilterRegistrationBean<CmsSecurityFilter> registration = new FilterRegistrationBean<>();
        registration.setFilter(new CmsSecurityFilter(properties, cmsReplayRequestStore, cmsTokenService));
        registration.setOrder(Integer.MIN_VALUE + 10);
        registration.addUrlPatterns("/*");
        return registration;
    }
}
