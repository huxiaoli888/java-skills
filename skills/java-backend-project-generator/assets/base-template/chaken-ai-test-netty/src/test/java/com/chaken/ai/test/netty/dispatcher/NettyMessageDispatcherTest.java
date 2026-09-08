package com.chaken.ai.test.netty.dispatcher;

import static org.assertj.core.api.Assertions.assertThat;

import com.chaken.ai.test.netty.handler.HeartbeatMessageHandler;
import com.chaken.ai.test.netty.protocol.NettyMessageEnvelope;
import com.chaken.ai.test.netty.protocol.NettyResponseWriter;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.List;
import org.junit.jupiter.api.Test;

class NettyMessageDispatcherTest {

    @Test
    void dispatchesHeartbeatWithUnifiedResponse() {
        NettyResponseWriter responseWriter = new NettyResponseWriter(new ObjectMapper());
        NettyMessageDispatcher dispatcher = new NettyMessageDispatcher(List.of(new HeartbeatMessageHandler()), responseWriter);
        NettyMessageEnvelope envelope = new NettyMessageEnvelope();
        envelope.setReqid("req-1");
        envelope.setFunc("HEARTBEAT");
        envelope.setVersion("V1");
        envelope.setTs(System.currentTimeMillis());

        String response = dispatcher.dispatch(envelope);

        assertThat(response).contains("\"reqid\":\"req-1\"");
        assertThat(response).contains("\"code\":\"000000\"");
        assertThat(response).contains("\"ackFunc\":\"HEARTBEAT\"");
        assertThat(response).contains("\"ackStatus\":\"RECEIVED\"");
    }

    @Test
    void missingReqidShouldReturnServerGeneratedReqid() {
        NettyResponseWriter responseWriter = new NettyResponseWriter(new ObjectMapper());
        NettyMessageDispatcher dispatcher = new NettyMessageDispatcher(List.of(new HeartbeatMessageHandler()), responseWriter);
        NettyMessageEnvelope envelope = new NettyMessageEnvelope();
        envelope.setFunc("HEARTBEAT");
        envelope.setVersion("V1");
        envelope.setTs(System.currentTimeMillis());

        String response = dispatcher.dispatch(envelope);

        assertThat(response).contains("\"code\":\"AC0001\"");
        assertThat(response).contains("\"reqid\":\"server-");
        assertThat(response).doesNotContain("\"reqid\":null");
        assertThat(response).doesNotContain("\"reqid\":\"\"");
    }

    @Test
    void parsesHyphenatedSecurityFields() throws Exception {
        ObjectMapper objectMapper = new ObjectMapper();
        String json = """
                {
                  "reqid": "req-1",
                  "func": "AUTH",
                  "version": "V1",
                  "ts": 1785227732173,
                  "udid": "device-1",
                  "authorization": "Bearer token",
                  "sign": "signature",
                  "sign-alg": "HMAC-SHA256",
                  "api-key": "dev-api-key",
                  "payload": {"seqno": 1}
                }
                """;

        NettyMessageEnvelope envelope = objectMapper.readValue(json, NettyMessageEnvelope.class);

        assertThat(envelope.getSignAlg()).isEqualTo("HMAC-SHA256");
        assertThat(envelope.getApiKey()).isEqualTo("dev-api-key");
        assertThat(envelope.getPayload().get("seqno").asInt()).isEqualTo(1);
    }
}
