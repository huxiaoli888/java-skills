package com.chaken.ai.test.common.security.sql;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Pattern;

public class SqlInjectionGuard {
    private final List<Pattern> blockedPatterns;

    public SqlInjectionGuard(List<String> blockedPatterns) {
        this.blockedPatterns = new ArrayList<>();
        for (String blockedPattern : blockedPatterns) {
            this.blockedPatterns.add(Pattern.compile(blockedPattern));
        }
    }

    public boolean hasInjectionRisk(String value) {
        if (value == null || value.isBlank()) {
            return false;
        }
        for (Pattern pattern : blockedPatterns) {
            if (pattern.matcher(value).matches()) {
                return true;
            }
        }
        return false;
    }
}
