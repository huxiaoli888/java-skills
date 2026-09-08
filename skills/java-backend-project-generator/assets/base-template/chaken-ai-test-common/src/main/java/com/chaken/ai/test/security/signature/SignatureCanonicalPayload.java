package com.chaken.ai.test.security.signature;

import jakarta.servlet.http.HttpServletRequest;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.Comparator;

public final class SignatureCanonicalPayload {
    private SignatureCanonicalPayload() {
    }

    public static String query(HttpServletRequest request) {
        return canonicalUrlEncoded(request == null ? null : request.getQueryString());
    }

    public static byte[] body(HttpServletRequest request, byte[] rawBody) {
        return rawBody == null ? new byte[0] : rawBody;
    }

    public static String canonicalUrlEncoded(String value) {
        if (isBlank(value)) {
            return "";
        }
        return Arrays.stream(value.split("&"))
                .filter(part -> !part.isBlank())
                .sorted(Comparator.comparing(SignatureCanonicalPayload::pairKey)
                        .thenComparing(SignatureCanonicalPayload::pairValue))
                .reduce((left, right) -> left + "&" + right)
                .orElse("");
    }

    private static String pairKey(String pair) {
        int index = pair.indexOf('=');
        return decode(index < 0 ? pair : pair.substring(0, index));
    }

    private static String pairValue(String pair) {
        int index = pair.indexOf('=');
        return decode(index < 0 ? "" : pair.substring(index + 1));
    }

    private static String decode(String value) {
        return URLDecoder.decode(value, StandardCharsets.UTF_8);
    }

    private static boolean isBlank(String value) {
        return value == null || value.trim().isEmpty();
    }
}
