package com.chaken.ai.test.netty.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "chaken.netty")
public class NettyServerProperties {
    private final Tcp tcp = new Tcp();
    private final Udp udp = new Udp();
    private final Security security = new Security();

    public Tcp getTcp() {
        return tcp;
    }

    public Udp getUdp() {
        return udp;
    }

    public Security getSecurity() {
        return security;
    }

    public static class Tcp {
        private boolean enabled = true;
        private int port = 19090;
        private int authTimeoutMs = 5000;
        private int readerIdleSeconds = 60;
        private int maxFrameBytes = 65536;

        public boolean isEnabled() {
            return enabled;
        }

        public void setEnabled(boolean enabled) {
            this.enabled = enabled;
        }

        public int getPort() {
            return port;
        }

        public void setPort(int port) {
            this.port = port;
        }

        public int getAuthTimeoutMs() {
            return authTimeoutMs;
        }

        public void setAuthTimeoutMs(int authTimeoutMs) {
            this.authTimeoutMs = authTimeoutMs;
        }

        public int getReaderIdleSeconds() {
            return readerIdleSeconds;
        }

        public void setReaderIdleSeconds(int readerIdleSeconds) {
            this.readerIdleSeconds = readerIdleSeconds;
        }

        public int getMaxFrameBytes() {
            return maxFrameBytes;
        }

        public void setMaxFrameBytes(int maxFrameBytes) {
            this.maxFrameBytes = maxFrameBytes;
        }
    }

    public static class Udp {
        private boolean enabled = true;
        private int port = 19091;
        private int maxDatagramBytes = 2048;
        private int routeTtlSeconds = 60;

        public boolean isEnabled() {
            return enabled;
        }

        public void setEnabled(boolean enabled) {
            this.enabled = enabled;
        }

        public int getPort() {
            return port;
        }

        public void setPort(int port) {
            this.port = port;
        }

        public int getMaxDatagramBytes() {
            return maxDatagramBytes;
        }

        public void setMaxDatagramBytes(int maxDatagramBytes) {
            this.maxDatagramBytes = maxDatagramBytes;
        }

        public int getRouteTtlSeconds() {
            return routeTtlSeconds;
        }

        public void setRouteTtlSeconds(int routeTtlSeconds) {
            this.routeTtlSeconds = routeTtlSeconds;
        }
    }

    public static class Security {
        private long timestampSkewSeconds = 300;
        private long replayTtlSeconds = 300;
        private String devApiKey = "dev-netty-api-key";
        private String devToken = "dev-netty-token";

        public long getTimestampSkewSeconds() {
            return timestampSkewSeconds;
        }

        public void setTimestampSkewSeconds(long timestampSkewSeconds) {
            this.timestampSkewSeconds = timestampSkewSeconds;
        }

        public long getReplayTtlSeconds() {
            return replayTtlSeconds;
        }

        public void setReplayTtlSeconds(long replayTtlSeconds) {
            this.replayTtlSeconds = replayTtlSeconds;
        }

        public String getDevApiKey() {
            return devApiKey;
        }

        public void setDevApiKey(String devApiKey) {
            this.devApiKey = devApiKey;
        }

        public String getDevToken() {
            return devToken;
        }

        public void setDevToken(String devToken) {
            this.devToken = devToken;
        }
    }
}
