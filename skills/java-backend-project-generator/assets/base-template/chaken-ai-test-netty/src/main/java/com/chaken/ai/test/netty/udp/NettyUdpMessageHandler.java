package com.chaken.ai.test.netty.udp;

import com.chaken.ai.test.netty.dispatcher.NettyMessageDispatcher;
import com.chaken.ai.test.netty.protocol.NettyMessageEnvelope;
import com.chaken.ai.test.netty.protocol.NettyResponseWriter;
import com.chaken.ai.test.netty.security.NettyAuthenticationException;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.netty.buffer.Unpooled;
import io.netty.channel.ChannelHandler;
import io.netty.channel.ChannelHandlerContext;
import io.netty.channel.SimpleChannelInboundHandler;
import io.netty.channel.socket.DatagramPacket;
import java.nio.charset.StandardCharsets;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

@Component
@ChannelHandler.Sharable
public class NettyUdpMessageHandler extends SimpleChannelInboundHandler<DatagramPacket> {
    private static final Logger log = LoggerFactory.getLogger(NettyUdpMessageHandler.class);

    private final ObjectMapper objectMapper;
    private final NettyMessageDispatcher dispatcher;
    private final NettyResponseWriter responseWriter;

    public NettyUdpMessageHandler(ObjectMapper objectMapper, NettyMessageDispatcher dispatcher, NettyResponseWriter responseWriter) {
        this.objectMapper = objectMapper;
        this.dispatcher = dispatcher;
        this.responseWriter = responseWriter;
    }

    @Override
    protected void channelRead0(ChannelHandlerContext context, DatagramPacket packet) {
        long start = System.currentTimeMillis();
        String reqid = "";
        try {
            String message = packet.content().toString(StandardCharsets.UTF_8);
            NettyMessageEnvelope envelope = objectMapper.readValue(message, NettyMessageEnvelope.class);
            reqid = envelope.getReqid();
            String response = dispatcher.dispatch(envelope);
            context.writeAndFlush(new DatagramPacket(Unpooled.copiedBuffer(response, StandardCharsets.UTF_8), packet.sender()));
            log.info("netty_udp_message reqid={} func={} version={} sender={} durationMs={}", envelope.getReqid(), envelope.getFunc(), envelope.getVersion(), packet.sender(), System.currentTimeMillis() - start);
        } catch (NettyAuthenticationException ex) {
            log.info("netty_udp_auth_failed reqid={} sender={} durationMs={} code={}", reqid, packet.sender(), System.currentTimeMillis() - start, "AC0002");
            writeError(context, packet, responseWriter.fail(reqid, "AC0002", ex.getMessage()));
        } catch (JsonProcessingException ex) {
            writeError(context, packet, responseWriter.fail(reqid, "AC0001", "协议格式错误"));
            log.info("netty_udp_protocol_invalid reqid={} sender={} durationMs={} code={}", reqid, packet.sender(), System.currentTimeMillis() - start, "AC0001");
        } catch (Exception ex) {
            log.error("netty_udp_message_failed reqid={} sender={} durationMs={}", reqid, packet.sender(), System.currentTimeMillis() - start, ex);
            writeError(context, packet, responseWriter.fail(reqid, "AC9999", "系统异常"));
        }
    }

    private void writeError(ChannelHandlerContext context, DatagramPacket packet, String response) {
        context.writeAndFlush(new DatagramPacket(Unpooled.copiedBuffer(response, StandardCharsets.UTF_8), packet.sender()));
    }
}
