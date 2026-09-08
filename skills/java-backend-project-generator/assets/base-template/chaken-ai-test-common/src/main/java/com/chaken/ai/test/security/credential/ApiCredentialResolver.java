package com.chaken.ai.test.security.credential;

import java.util.Optional;

public interface ApiCredentialResolver {
    Optional<ApiCredential> resolve(String apiKey);
}
