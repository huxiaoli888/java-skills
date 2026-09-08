package com.chaken.ai.test.security.signature;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.Base64;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

public final class RequestSigner {
    private RequestSigner() {
    }

    public static byte[] canonicalBytes(
            String method,
            String path,
            String canonicalQuery,
            String timestamp,
            String reqid,
            String apiKey,
            String udid,
            String signatureAlg,
            String apiVersion,
            byte[] rawBody) {
        byte[] prefix = (joinLines(
                method == null ? "" : method.toUpperCase(),
                path,
                canonicalQuery,
                timestamp,
                reqid,
                apiKey,
                udid,
                signatureAlg,
                apiVersion) + "\n").getBytes(StandardCharsets.UTF_8);
        byte[] body = rawBody == null ? new byte[0] : rawBody;
        byte[] result = Arrays.copyOf(prefix, prefix.length + body.length);
        System.arraycopy(body, 0, result, prefix.length, body.length);
        return result;
    }

    public static String hmacSha256Base64(String secret, byte[] canonicalBytes) {
        try {
            Mac mac = Mac.getInstance("HmacSHA256");
            mac.init(new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256"));
            byte[] signature = mac.doFinal(canonicalBytes == null ? new byte[0] : canonicalBytes);
            return Base64.getEncoder().encodeToString(signature);
        } catch (Exception ex) {
            throw new IllegalStateException("请求签名失败", ex);
        }
    }

    public static boolean constantTimeEquals(String expected, String actual) {
        if (expected == null || actual == null) {
            return false;
        }
        return MessageDigest.isEqual(
                expected.getBytes(StandardCharsets.UTF_8),
                actual.getBytes(StandardCharsets.UTF_8));
    }

    private static String joinLines(String... parts) {
        StringBuilder builder = new StringBuilder();
        for (int i = 0; i < parts.length; i++) {
            if (i > 0) {
                builder.append('\n');
            }
            builder.append(parts[i] == null ? "" : parts[i]);
        }
        return builder.toString();
    }
}
