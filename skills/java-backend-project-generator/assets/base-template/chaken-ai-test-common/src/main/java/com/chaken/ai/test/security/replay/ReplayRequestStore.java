package com.chaken.ai.test.security.replay;

import java.time.Duration;

public interface ReplayRequestStore {
    boolean saveIfAbsent(String replaySubject, String reqid, Duration ttl);
}
