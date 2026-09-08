package com.chaken.ai.test.netty.tcp;

import com.chaken.ai.test.netty.dispatcher.NettyMessageDispatcher;
import com.chaken.ai.test.netty.protocol.NettyMessageEnvelope;
import com.chaken.ai.test.netty.protocol.NettyResponseWriter;
import com.chaken.ai.test.netty.security.NettyAuthenticationException;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.netty.channel.ChannelHandler;
import io.netty.channel.ChannelHandlerContext;
import io.netty.channel.SimpleChannelInboundHandler;
import io.netty.handler.timeout.IdleStateEvent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

@Component
@ChannelHandler.Sharable
public class NettyTcpMessageHandler extends SimpleChannelInboundHandler<String> {
    private static final Logger log = LoggerFactory.getLogger(NettyTcpMessageHandler.class);

    private final ObjectMapper objectMapper;
    private final NettyMessageDispatcher dispatcher;
    private final NettyResponseWriter responseWriter;

    public NettyTcpMessageHandler(ObjectMapper objectMapper, NettyMessageDispatcher dispatcher, NettyResponseWriter responseWriter) {
        this.objectMapper = objectMapper;
        this.dispatcher = dispatcher;
        this.responseWriter = responseWriter;
    }

    @Override
    protected void channelRead0(ChannelHandlerContext context, String message) {
        long start = System.currentTimeMillis();
        String reqid = "";
        try {
            NettyMessageEnvelope envelope = objectMapper.readValue(message, NettyMessageEnvelope.class);
            reqid = envelope.getReqid();
            String response = dispatcher.dispatch(envelope);
            context.writeAndFlush(response + "\n");
            log.info("netty_tcp_message reqid={} func={} version={} durationMs={}", envelope.getReqid(), envelope.getFunc(), envelope.getVersion(), System.currentTimeMillis() - start);
        } catch (NettyAuthenticationException ex) {
            log.info("netty_tcp_auth_failed reqid={} durationMs={} code={}", reqid, System.currentTimeMillis() - start, "AC0002");
            context.writeAndFlush(responseWriter.fail(reqid, "AC0002", ex.getMessage()) + "\n");
        } catch (JsonProcessingException ex) {
            context.writeAndFlush(responseWriter.fail(reqid, "AC0001", "协议格式错误") + "\n");
            log.info("netty_tcp_protocol_invalid reqid={} durationMs={} code={}", reqid, System.currentTimeMillis() - start, "AC0001");
        } catch (Exception ex) {
            log.error("netty_tcp_message_failed reqid={} durationMs={}", reqid, System.currentTimeMillis() - start, ex);
            context.writeAndFlush(responseWriter.fail(reqid, "AC9999", "系统异常") + "\n");
        }
    }

    @Override
    public void userEventTriggered(ChannelHandlerContext context, Object event) {
        if (event instanceof IdleStateEvent) {
            log.info("netty_tcp_idle_close channelId={}", context.channel().id().asShortText());
            context.close();
        } else {
            context.fireUserEventTriggered(event);
        }
    }
}
