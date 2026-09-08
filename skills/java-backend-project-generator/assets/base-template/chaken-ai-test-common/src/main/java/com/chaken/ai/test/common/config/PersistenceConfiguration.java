package com.chaken.ai.test.common.config;

import com.chaken.ai.test.common.persistence.EntityAuditFillSupport;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class PersistenceConfiguration {
    @Bean
    public EntityAuditFillSupport entityAuditFillSupport() {
        return new EntityAuditFillSupport();
    }
}
