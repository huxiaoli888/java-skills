package com.chaken.ai.test.netty.dispatcher;

import java.util.Objects;

public final class MessageKey {
    private final String func;
    private final String version;

    public MessageKey(String func, String version) {
        this.func = normalize(func);
        this.version = normalize(version);
    }

    public String getFunc() {
        return func;
    }

    public String getVersion() {
        return version;
    }

    @Override
    public boolean equals(Object other) {
        if (this == other) {
            return true;
        }
        if (!(other instanceof MessageKey)) {
            return false;
        }
        MessageKey that = (MessageKey) other;
        return Objects.equals(func, that.func) && Objects.equals(version, that.version);
    }

    @Override
    public int hashCode() {
        return Objects.hash(func, version);
    }

    private static String normalize(String value) {
        return value == null ? "" : value.trim().toUpperCase();
    }
}
