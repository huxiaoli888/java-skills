package com.chaken.ai.test.netty.udp;

import com.chaken.ai.test.netty.config.NettyServerProperties;
import io.netty.bootstrap.Bootstrap;
import io.netty.channel.Channel;
import io.netty.channel.EventLoopGroup;
import io.netty.channel.nio.NioEventLoopGroup;
import io.netty.channel.socket.nio.NioDatagramChannel;
import jakarta.annotation.PreDestroy;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

@Component
public class NettyUdpServer {
    private static final Logger log = LoggerFactory.getLogger(NettyUdpServer.class);

    private final NettyServerProperties properties;
    private final NettyUdpMessageHandler messageHandler;
    private EventLoopGroup group;
    private Channel channel;

    public NettyUdpServer(NettyServerProperties properties, NettyUdpMessageHandler messageHandler) {
        this.properties = properties;
        this.messageHandler = messageHandler;
    }

    @EventListener(ApplicationReadyEvent.class)
    public void start() throws InterruptedException {
        if (!properties.getUdp().isEnabled()) {
            log.info("netty_udp_disabled");
            return;
        }
        group = new NioEventLoopGroup();
        Bootstrap bootstrap = new Bootstrap()
            .group(group)
            .channel(NioDatagramChannel.class)
            .handler(messageHandler);
        channel = bootstrap.bind(properties.getUdp().getPort()).sync().channel();
        log.info("netty_udp_started port={}", properties.getUdp().getPort());
    }

    @PreDestroy
    public void stop() {
        if (channel != null) {
            channel.close();
        }
        if (group != null) {
            group.shutdownGracefully();
        }
        log.info("netty_udp_stopped");
    }
}
