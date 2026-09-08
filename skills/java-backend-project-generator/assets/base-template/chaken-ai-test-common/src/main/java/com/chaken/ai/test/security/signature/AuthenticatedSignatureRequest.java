package com.chaken.ai.test.security.signature;

import com.chaken.ai.test.security.body.CachedBodyHttpServletRequest;
import com.chaken.ai.test.security.credential.ApiCredential;

public record AuthenticatedSignatureRequest(
        CachedBodyHttpServletRequest request,
        ApiCredential credential,
        String requestFingerprint) {
}
