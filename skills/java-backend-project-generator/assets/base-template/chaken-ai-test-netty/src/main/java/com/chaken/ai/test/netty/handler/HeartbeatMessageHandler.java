package com.chaken.ai.test.netty.handler;

import com.chaken.ai.test.netty.dispatcher.MessageKey;
import com.chaken.ai.test.netty.dispatcher.NettyMessageHandler;
import com.chaken.ai.test.netty.protocol.NettyMessageEnvelope;
import java.util.LinkedHashMap;
import java.util.Map;
import org.springframework.stereotype.Component;

@Component
public class HeartbeatMessageHandler implements NettyMessageHandler {
    @Override
    public MessageKey key() {
        return new MessageKey("HEARTBEAT", "V1");
    }

    @Override
    public Object handle(NettyMessageEnvelope envelope) {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("ackFunc", "HEARTBEAT");
        data.put("ackStatus", "RECEIVED");
        data.put("serverTime", System.currentTimeMillis());
        return data;
    }
}
