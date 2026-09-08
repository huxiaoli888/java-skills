package com.chaken.ai.test.netty;

import com.chaken.ai.test.netty.config.NettyServerProperties;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;

@SpringBootApplication
@EnableConfigurationProperties(NettyServerProperties.class)
public class ChakenAiTestNettyApplication {

    public static void main(String[] args) {
        SpringApplication.run(ChakenAiTestNettyApplication.class, args);
    }
}
