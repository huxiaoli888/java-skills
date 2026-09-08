package com.chaken.ai.test.common.logging;

import java.util.List;
import java.util.regex.Pattern;

public class RequestBodyMasker {
    private final List<Pattern> jsonPatterns;
    private final List<Pattern> formPatterns;

    public RequestBodyMasker(List<String> sensitiveKeys) {
        String keyRegex = String.join("|", sensitiveKeys);
        this.jsonPatterns = List.of(
                Pattern.compile("(\"(?:" + keyRegex + ")\"\\s*:\\s*\")([^\"]*)(\")", Pattern.CASE_INSENSITIVE),
                Pattern.compile("(\"(?:" + keyRegex + ")\"\\s*:\\s*)([^,\"}\\s]+)([,}\\s])", Pattern.CASE_INSENSITIVE));
        this.formPatterns = List.of(
                Pattern.compile("((?:^|[&?])(?:" + keyRegex + ")=)([^&]*)", Pattern.CASE_INSENSITIVE));
    }

    public static RequestBodyMasker defaultMasker() {
        return new RequestBodyMasker(List.of(
                "password",
                "oldPassword",
                "newPassword",
                "token",
                "accessToken",
                "refreshToken",
                "authorization",
                "secret",
                "privateKey",
                "captcha",
                "captchaCode",
                "smsCode",
                "verifyCode",
                "idCard",
                "bankCard",
                "cardNo"));
    }

    public String mask(String body) {
        if (body == null || body.isEmpty()) {
            return "";
        }
        String masked = body;
        for (Pattern pattern : jsonPatterns) {
            masked = pattern.matcher(masked).replaceAll("$1***$3");
        }
        for (Pattern pattern : formPatterns) {
            masked = pattern.matcher(masked).replaceAll("$1***");
        }
        return masked;
    }
}
