package com.chaken.ai.test.netty.dispatcher;

import com.chaken.ai.test.netty.protocol.NettyMessageEnvelope;

public interface NettyMessageHandler {
    MessageKey key();

    Object handle(NettyMessageEnvelope envelope);
}
