package com.chaken.ai.test.netty.tcp;

import com.chaken.ai.test.netty.config.NettyServerProperties;
import io.netty.bootstrap.ServerBootstrap;
import io.netty.channel.Channel;
import io.netty.channel.EventLoopGroup;
import io.netty.channel.nio.NioEventLoopGroup;
import io.netty.channel.socket.nio.NioServerSocketChannel;
import jakarta.annotation.PreDestroy;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

@Component
public class NettyTcpServer {
    private static final Logger log = LoggerFactory.getLogger(NettyTcpServer.class);

    private final NettyServerProperties properties;
    private final NettyTcpChannelInitializer channelInitializer;
    private EventLoopGroup bossGroup;
    private EventLoopGroup workerGroup;
    private Channel serverChannel;

    public NettyTcpServer(NettyServerProperties properties, NettyTcpChannelInitializer channelInitializer) {
        this.properties = properties;
        this.channelInitializer = channelInitializer;
    }

    @EventListener(ApplicationReadyEvent.class)
    public void start() throws InterruptedException {
        if (!properties.getTcp().isEnabled()) {
            log.info("netty_tcp_disabled");
            return;
        }
        bossGroup = new NioEventLoopGroup(1);
        workerGroup = new NioEventLoopGroup();
        ServerBootstrap bootstrap = new ServerBootstrap()
            .group(bossGroup, workerGroup)
            .channel(NioServerSocketChannel.class)
            .childHandler(channelInitializer);
        serverChannel = bootstrap.bind(properties.getTcp().getPort()).sync().channel();
        log.info("netty_tcp_started port={}", properties.getTcp().getPort());
    }

    @PreDestroy
    public void stop() {
        if (serverChannel != null) {
            serverChannel.close();
        }
        if (bossGroup != null) {
            bossGroup.shutdownGracefully();
        }
        if (workerGroup != null) {
            workerGroup.shutdownGracefully();
        }
        log.info("netty_tcp_stopped");
    }
}
