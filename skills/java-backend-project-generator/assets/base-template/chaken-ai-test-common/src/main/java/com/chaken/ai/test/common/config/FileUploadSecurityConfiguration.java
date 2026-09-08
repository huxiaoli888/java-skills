package com.chaken.ai.test.common.config;

import com.chaken.ai.test.common.security.file.FileUploadSecurityPolicy;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
@EnableConfigurationProperties(FileUploadSecurityProperties.class)
public class FileUploadSecurityConfiguration {
    @Bean
    public FileUploadSecurityPolicy fileUploadSecurityPolicy(FileUploadSecurityProperties properties) {
        return new FileUploadSecurityPolicy(properties);
    }
}
