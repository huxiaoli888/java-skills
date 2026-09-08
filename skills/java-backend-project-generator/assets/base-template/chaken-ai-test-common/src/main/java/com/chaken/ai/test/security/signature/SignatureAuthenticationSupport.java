package com.chaken.ai.test.security.signature;

import com.chaken.ai.test.common.code.CommonErrorCode;
import com.chaken.ai.test.security.body.CachedBodyHttpServletRequest;
import com.chaken.ai.test.security.credential.ApiCredential;
import com.chaken.ai.test.security.credential.ApiCredentialResolver;
import com.chaken.ai.test.security.replay.ReplayRequestStore;
import jakarta.servlet.http.HttpServletRequest;
import java.io.IOException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Duration;
import java.time.Instant;
import java.util.Base64;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.util.StreamUtils;

public class SignatureAuthenticationSupport {
    private static final Logger log = LoggerFactory.getLogger(SignatureAuthenticationSupport.class);
    public static final String REQUEST_FINGERPRINT_ATTRIBUTE =
            SignatureAuthenticationSupport.class.getName() + ".requestFingerprint";
    public static final String CREDENTIAL_ATTRIBUTE = ApiCredential.class.getName();
    private static final String SIGNATURE_ALG = "HMAC-SHA256";
    private static final String EXPECTED_SIGNED_HEADERS =
            "x-timestamp;x-reqid;x-api-key;x-udid;x-sign-alg;x-api-version";

    private final ApiCredentialResolver apiCredentialResolver;
    private final ReplayRequestStore replayRequestStore;

    public SignatureAuthenticationSupport(
            ApiCredentialResolver apiCredentialResolver,
            ReplayRequestStore replayRequestStore) {
        this.apiCredentialResolver = apiCredentialResolver;
        this.replayRequestStore = replayRequestStore;
    }

    public AuthenticatedSignatureRequest authenticate(HttpServletRequest request, Duration replayWindow)
            throws IOException {
        String apiKey = request.getHeader(SignatureHeaders.API_KEY);
        String timestamp = request.getHeader(SignatureHeaders.TIMESTAMP);
        String reqid = request.getHeader(SignatureHeaders.REQID);
        String udid = request.getHeader(SignatureHeaders.UDID);
        String signatureAlg = request.getHeader(SignatureHeaders.SIGNATURE_ALG);
        String apiVersion = request.getHeader(SignatureHeaders.API_VERSION);
        String signature = request.getHeader(SignatureHeaders.SIGN);

        if (isBlank(apiKey) || isBlank(timestamp) || isBlank(reqid) || isBlank(signatureAlg)
                || isBlank(apiVersion) || isBlank(signature)) {
            throw new SignatureAuthenticationException(CommonErrorCode.PARAM_INVALID);
        }
        if (!SIGNATURE_ALG.equalsIgnoreCase(signatureAlg)) {
            throw new SignatureAuthenticationException(CommonErrorCode.SIGNATURE_INVALID);
        }
        if (isExpired(timestamp, replayWindow)) {
            throw new SignatureAuthenticationException(CommonErrorCode.REQUEST_EXPIRED);
        }

        Optional<ApiCredential> credential = apiCredentialResolver.resolve(apiKey);
        if (credential.isEmpty()) {
            throw new SignatureAuthenticationException(CommonErrorCode.UNAUTHORIZED);
        }

        CachedBodyHttpServletRequest wrappedRequest = cachedRequest(request);
        byte[] canonicalBody = SignatureCanonicalPayload.body(request, wrappedRequest.getCachedBody());
        byte[] canonicalBytes = RequestSigner.canonicalBytes(
                request.getMethod(),
                request.getRequestURI(),
                SignatureCanonicalPayload.query(request),
                timestamp,
                reqid,
                apiKey,
                udid,
                signatureAlg,
                apiVersion,
                canonicalBody);
        String expectedSignature = RequestSigner.hmacSha256Base64(credential.get().secret(), canonicalBytes);
        if (!RequestSigner.constantTimeEquals(expectedSignature, signature)) {
            throw new SignatureAuthenticationException(CommonErrorCode.SIGNATURE_INVALID);
        }

        if (!replayRequestStore.saveIfAbsent(apiKey, reqid, replayWindow)) {
            throw new SignatureAuthenticationException(CommonErrorCode.REPLAY_REQUEST);
        }

        String requestFingerprint = fingerprint(canonicalBytes);
        wrappedRequest.setAttribute(CREDENTIAL_ATTRIBUTE, credential.get());
        wrappedRequest.setAttribute(REQUEST_FINGERPRINT_ATTRIBUTE, requestFingerprint);
        return new AuthenticatedSignatureRequest(wrappedRequest, credential.get(), requestFingerprint);
    }

    public boolean hasSignatureHeaders(HttpServletRequest request) {
        return !isBlank(request.getHeader(SignatureHeaders.API_KEY))
                || !isBlank(request.getHeader(SignatureHeaders.REQID))
                || !isBlank(request.getHeader(SignatureHeaders.SIGN))
                || !isBlank(request.getHeader(SignatureHeaders.SIGNATURE_ALG));
    }

    private boolean isExpired(String timestamp, Duration replayWindow) {
        try {
            Instant requestTime = parseTimestamp(timestamp);
            Instant now = Instant.now();
            return requestTime.isBefore(now.minus(replayWindow)) || requestTime.isAfter(now.plus(replayWindow));
        } catch (RuntimeException ex) {
            log.info("signature_timestamp_invalid");
            return true;
        }
    }

    private CachedBodyHttpServletRequest cachedRequest(HttpServletRequest request) throws IOException {
        if (request instanceof CachedBodyHttpServletRequest cachedRequest) {
            return cachedRequest;
        }
        byte[] rawBody = StreamUtils.copyToByteArray(request.getInputStream());
        return new CachedBodyHttpServletRequest(request, rawBody);
    }

    private Instant parseTimestamp(String timestamp) {
        if (timestamp.matches("\\d+")) {
            return Instant.ofEpochMilli(Long.parseLong(timestamp));
        }
        return Instant.parse(timestamp);
    }

    private String fingerprint(byte[] canonicalBytes) {
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256").digest(canonicalBytes);
            return Base64.getEncoder().encodeToString(digest);
        } catch (NoSuchAlgorithmException ex) {
            throw new IllegalStateException("SHA-256 不可用", ex);
        }
    }

    private boolean isBlank(String value) {
        return value == null || value.trim().isEmpty();
    }
}
