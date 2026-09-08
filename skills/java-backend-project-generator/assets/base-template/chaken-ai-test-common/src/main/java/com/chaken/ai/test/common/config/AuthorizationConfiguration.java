package com.chaken.ai.test.common.config;

import com.chaken.ai.test.common.permission.service.DefaultPermissionEvaluator;
import com.chaken.ai.test.common.permission.aspect.PermissionAuthorizationAspect;
import com.chaken.ai.test.common.permission.service.PermissionEvaluator;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class AuthorizationConfiguration {
    @Bean
    @ConditionalOnMissingBean
    PermissionEvaluator permissionEvaluator() {
        return new DefaultPermissionEvaluator();
    }

    @Bean
    @ConditionalOnMissingBean
    PermissionAuthorizationAspect permissionAuthorizationAspect(PermissionEvaluator permissionEvaluator) {
        return new PermissionAuthorizationAspect(permissionEvaluator);
    }
}

