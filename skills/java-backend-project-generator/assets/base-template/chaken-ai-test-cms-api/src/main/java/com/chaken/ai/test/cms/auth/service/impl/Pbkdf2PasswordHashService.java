package com.chaken.ai.test.cms.auth.service.impl;

import com.chaken.ai.test.cms.auth.service.PasswordHashService;
import java.security.MessageDigest;
import java.util.Base64;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

@Service
public class Pbkdf2PasswordHashService implements PasswordHashService {
    private static final Logger log = LoggerFactory.getLogger(Pbkdf2PasswordHashService.class);
    private static final String ALGORITHM = "PBKDF2WithHmacSHA256";
    private static final int ITERATIONS = 120_000;
    private static final int KEY_LENGTH = 256;

    @Override
    public boolean matches(String rawPassword, String saltBase64, String expectedHashBase64) {
        if (isBlank(rawPassword) || isBlank(saltBase64) || isBlank(expectedHashBase64)) {
            return false;
        }
        try {
            byte[] salt = Base64.getDecoder().decode(saltBase64);
            byte[] expected = Base64.getDecoder().decode(expectedHashBase64);
            PBEKeySpec spec = new PBEKeySpec(rawPassword.toCharArray(), salt, ITERATIONS, KEY_LENGTH);
            byte[] actual = SecretKeyFactory.getInstance(ALGORITHM).generateSecret(spec).getEncoded();
            return MessageDigest.isEqual(actual, expected);
        } catch (RuntimeException | java.security.GeneralSecurityException ex) {
            log.error("cms password hash verification failed", ex);
            return false;
        }
    }

    private boolean isBlank(String value) {
        return value == null || value.trim().isEmpty();
    }
}
