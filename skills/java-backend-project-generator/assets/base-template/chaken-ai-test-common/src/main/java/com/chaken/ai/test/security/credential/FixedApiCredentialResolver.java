package com.chaken.ai.test.security.credential;

import java.util.Optional;

public class FixedApiCredentialResolver implements ApiCredentialResolver {
    private final String apiKey;
    private final String secret;

    public FixedApiCredentialResolver(String apiKey, String secret) {
        this.apiKey = apiKey;
        this.secret = secret;
    }

    @Override
    public Optional<ApiCredential> resolve(String apiKey) {
        if (apiKey == null || !apiKey.equals(this.apiKey)) {
            return Optional.empty();
        }
        return Optional.of(new ApiCredential(apiKey, secret));
    }
}
