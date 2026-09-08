package com.chaken.ai.test.netty.tcp;

import com.chaken.ai.test.netty.config.NettyServerProperties;
import io.netty.channel.ChannelInitializer;
import io.netty.channel.socket.SocketChannel;
import io.netty.handler.codec.LineBasedFrameDecoder;
import io.netty.handler.codec.string.StringDecoder;
import io.netty.handler.codec.string.StringEncoder;
import io.netty.handler.timeout.IdleStateHandler;
import java.nio.charset.StandardCharsets;
import org.springframework.stereotype.Component;

@Component
public class NettyTcpChannelInitializer extends ChannelInitializer<SocketChannel> {
    private final NettyServerProperties properties;
    private final NettyTcpMessageHandler messageHandler;

    public NettyTcpChannelInitializer(NettyServerProperties properties, NettyTcpMessageHandler messageHandler) {
        this.properties = properties;
        this.messageHandler = messageHandler;
    }

    @Override
    protected void initChannel(SocketChannel channel) {
        channel.pipeline()
            .addLast(new IdleStateHandler(properties.getTcp().getReaderIdleSeconds(), 0, 0))
            .addLast(new LineBasedFrameDecoder(properties.getTcp().getMaxFrameBytes()))
            .addLast(new StringDecoder(StandardCharsets.UTF_8))
            .addLast(new StringEncoder(StandardCharsets.UTF_8))
            .addLast(messageHandler);
    }
}
