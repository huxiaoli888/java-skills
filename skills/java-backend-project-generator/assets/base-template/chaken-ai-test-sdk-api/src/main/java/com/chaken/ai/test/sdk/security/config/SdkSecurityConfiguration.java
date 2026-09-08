package com.chaken.ai.test.sdk.security.config;

import com.chaken.ai.test.sdk.security.SdkSecurityFilter;
import com.chaken.ai.test.security.credential.ApiCredentialResolver;
import com.chaken.ai.test.security.credential.FixedApiCredentialResolver;
import com.chaken.ai.test.security.replay.InMemoryReplayRequestStore;
import com.chaken.ai.test.security.replay.ReplayRequestStore;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
@EnableConfigurationProperties(SdkSecurityProperties.class)
public class SdkSecurityConfiguration {
    @Bean
    public ApiCredentialResolver apiCredentialResolver(SdkSecurityProperties properties) {
        return new FixedApiCredentialResolver(properties.getDefaultApiKey(), properties.getDefaultSecret());
    }

    @Bean
    public ReplayRequestStore replayRequestStore() {
        return new InMemoryReplayRequestStore();
    }

    @Bean
    public FilterRegistrationBean<SdkSecurityFilter> sdkSecurityFilterRegistration(
            SdkSecurityProperties properties,
            ApiCredentialResolver apiCredentialResolver,
            ReplayRequestStore replayRequestStore) {
        FilterRegistrationBean<SdkSecurityFilter> registration = new FilterRegistrationBean<>();
        registration.setFilter(new SdkSecurityFilter(properties, apiCredentialResolver, replayRequestStore));
        registration.setOrder(Integer.MIN_VALUE + 10);
        registration.addUrlPatterns("/*");
        return registration;
    }
}
