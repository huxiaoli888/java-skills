package com.chaken.ai.test.netty.dispatcher;

import com.chaken.ai.test.netty.protocol.NettyMessageEnvelope;
import com.chaken.ai.test.netty.protocol.NettyResponseWriter;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Component;

@Component
public class NettyMessageDispatcher {
    private final Map<MessageKey, NettyMessageHandler> handlers = new HashMap<>();
    private final NettyResponseWriter responseWriter;

    public NettyMessageDispatcher(List<NettyMessageHandler> messageHandlers, NettyResponseWriter responseWriter) {
        this.responseWriter = responseWriter;
        for (NettyMessageHandler handler : messageHandlers) {
            NettyMessageHandler existing = handlers.putIfAbsent(handler.key(), handler);
            if (existing != null) {
                throw new IllegalStateException("Duplicate Netty message handler: " + handler.key().getFunc() + "/" + handler.key().getVersion());
            }
        }
    }

    public String dispatch(NettyMessageEnvelope envelope) {
        if (isBlank(envelope.getReqid()) || isBlank(envelope.getFunc()) || isBlank(envelope.getVersion())) {
            return responseWriter.fail(envelope.getReqid(), "AC0001", "协议字段缺失");
        }
        NettyMessageHandler handler = handlers.get(new MessageKey(envelope.getFunc(), envelope.getVersion()));
        if (handler == null) {
            return responseWriter.fail(envelope.getReqid(), "AC0007", "功能或版本不支持");
        }
        Object data = handler.handle(envelope);
        return responseWriter.success(envelope.getReqid(), data);
    }

    private boolean isBlank(String value) {
        return value == null || value.trim().isEmpty();
    }
}
