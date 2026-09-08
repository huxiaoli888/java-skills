package com.chaken.ai.test.cms.auth.service;

public interface PasswordHashService {
    boolean matches(String rawPassword, String saltBase64, String expectedHashBase64);
}
