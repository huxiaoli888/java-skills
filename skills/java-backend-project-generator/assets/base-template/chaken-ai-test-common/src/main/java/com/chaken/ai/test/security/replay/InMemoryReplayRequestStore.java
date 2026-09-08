package com.chaken.ai.test.security.replay;

import java.time.Duration;
import java.time.Instant;
import java.util.Iterator;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

public class InMemoryReplayRequestStore implements ReplayRequestStore {
    private final ConcurrentMap<String, Instant> requestExpireTimes = new ConcurrentHashMap<>();

    @Override
    public boolean saveIfAbsent(String replaySubject, String reqid, Duration ttl) {
        cleanupExpired();
        Instant expireTime = Instant.now().plus(ttl);
        return requestExpireTimes.putIfAbsent(replaySubject + ":" + reqid, expireTime) == null;
    }

    private void cleanupExpired() {
        Instant now = Instant.now();
        Iterator<Map.Entry<String, Instant>> iterator = requestExpireTimes.entrySet().iterator();
        while (iterator.hasNext()) {
            if (!iterator.next().getValue().isAfter(now)) {
                iterator.remove();
            }
        }
    }
}
