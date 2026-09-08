package com.chaken.ai.test.netty.security;

import com.chaken.ai.test.netty.config.NettyServerProperties;
import com.chaken.ai.test.netty.protocol.NettyMessageEnvelope;
import java.time.Instant;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;

@Component
public class NettyAuthenticationService {
    private final NettyServerProperties properties;

    public NettyAuthenticationService(NettyServerProperties properties) {
        this.properties = properties;
    }

    public void authenticate(NettyMessageEnvelope envelope) {
        require(StringUtils.hasText(envelope.getReqid()), "reqid 不能为空");
        require(StringUtils.hasText(envelope.getUdid()), "udid 不能为空");
        require(StringUtils.hasText(envelope.getApiKey()), "api-key 不能为空");
        require(StringUtils.hasText(envelope.getSign()), "sign 不能为空");
        require(StringUtils.hasText(envelope.getSignAlg()), "sign-alg 不能为空");
        require(timestampInWindow(envelope.getTs()), "ts 超出允许窗口");
        require(properties.getSecurity().getDevApiKey().equals(envelope.getApiKey()), "api-key 无效");
        if (StringUtils.hasText(envelope.getAuthorization())) {
            require(("Bearer " + properties.getSecurity().getDevToken()).equals(envelope.getAuthorization()), "authorization 无效");
        }
        // 开发模板只做字段和固定 key 校验；生产必须替换为 canonical 验签和分布式 replay cache。
    }

    private boolean timestampInWindow(long timestamp) {
        long now = Instant.now().toEpochMilli();
        long skew = properties.getSecurity().getTimestampSkewSeconds() * 1000L;
        return timestamp > 0 && Math.abs(now - timestamp) <= skew;
    }

    private void require(boolean condition, String message) {
        if (!condition) {
            throw new NettyAuthenticationException(message);
        }
    }
}
