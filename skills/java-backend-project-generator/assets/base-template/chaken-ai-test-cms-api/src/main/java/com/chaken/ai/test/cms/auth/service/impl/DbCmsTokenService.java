package com.chaken.ai.test.cms.auth.service.impl;

import com.chaken.ai.test.cms.auth.dto.response.CmsLoginResponse;
import com.chaken.ai.test.cms.auth.entity.AdminTokenEntity;
import com.chaken.ai.test.cms.auth.mapper.AdminTokenMapper;
import com.chaken.ai.test.cms.auth.service.CmsTokenService;
import com.chaken.ai.test.cms.security.AdminPrincipal;
import com.chaken.ai.test.cms.security.CmsSecurityProperties;
import com.chaken.ai.test.cms.sys.entity.SysUserEntity;
import com.chaken.ai.test.cms.sys.mapper.SysUserMapper;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.time.Instant;
import java.util.Base64;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import org.springframework.stereotype.Service;

@Service
public class DbCmsTokenService implements CmsTokenService {
    private static final String BEARER_PREFIX = "Bearer ";
    private static final SecureRandom SECURE_RANDOM = new SecureRandom();

    private final AdminTokenMapper tokenMapper;
    private final SysUserMapper userMapper;
    private final CmsSecurityProperties properties;

    public DbCmsTokenService(AdminTokenMapper tokenMapper, SysUserMapper userMapper, CmsSecurityProperties properties) {
        this.tokenMapper = tokenMapper;
        this.userMapper = userMapper;
        this.properties = properties;
    }

    @Override
    public CmsLoginResponse issueToken(SysUserEntity user, String udid) {
        String token = newToken();
        Instant now = Instant.now();
        Instant expireTime = now.plus(properties.getTokenTtl());
        AdminTokenEntity entity = new AdminTokenEntity();
        entity.setAdminId(user.getId());
        entity.setUsername(user.getUsername());
        entity.setTokenHash(hashToken(token));
        entity.setUdid(udid);
        entity.setStatus(1);
        entity.setExpireTime(expireTime);
        entity.setCreateTime(now);
        entity.setLastActiveTime(now);
        tokenMapper.insert(entity);
        return new CmsLoginResponse(token, expireTime, String.valueOf(user.getId()), user.getUsername());
    }

    @Override
    public Optional<AdminPrincipal> validateBearerToken(String authorization, String udid) {
        String token = rawBearerToken(authorization);
        if (token == null) {
            return Optional.empty();
        }
        AdminTokenEntity entity = tokenMapper.selectActiveToken(hashToken(token));
        if (entity == null || !entity.activeAt(Instant.now())) {
            return Optional.empty();
        }
        if (entity.getUdid() != null && udid != null && !entity.getUdid().equals(udid)) {
            return Optional.empty();
        }
        entity.setLastActiveTime(Instant.now());
        tokenMapper.updateById(entity);
        SysUserEntity user = userMapper.selectById(entity.getAdminId());
        if (user == null || !user.active()) {
            return Optional.empty();
        }
        Set<String> roles = roleCodes(entity.getAdminId(), user);
        Set<String> permissions = permissionCodes(entity.getAdminId(), user);
        return Optional.of(new AdminPrincipal(
                String.valueOf(entity.getAdminId()),
                entity.getUsername(),
                udid,
                "token",
                permissions,
                roles));
    }

    @Override
    public void revokeBearerToken(String authorization) {
        String token = rawBearerToken(authorization);
        if (token != null) {
            tokenMapper.revokeByTokenHash(hashToken(token));
        }
    }

    @Override
    public String tokenFingerprint(String authorization) {
        String token = rawBearerToken(authorization);
        return token == null ? "cms-token:anonymous" : "cms-token:" + hashToken(token);
    }

    private String newToken() {
        byte[] bytes = new byte[32];
        SECURE_RANDOM.nextBytes(bytes);
        return Base64.getUrlEncoder().withoutPadding().encodeToString(bytes);
    }

    private Set<String> roleCodes(Long userId, SysUserEntity user) {
        if (Boolean.TRUE.equals(user.getSuperAdmin())) {
            return Set.of("SUPER_ADMIN");
        }
        return new LinkedHashSet<>(userMapper.selectRoleCodes(userId));
    }

    private Set<String> permissionCodes(Long userId, SysUserEntity user) {
        if (Boolean.TRUE.equals(user.getSuperAdmin())) {
            return Set.of("*");
        }
        List<String> permissions = userMapper.selectPermissionCodes(userId);
        return new LinkedHashSet<>(permissions);
    }

    private String hashToken(String token) {
        byte[] digest;
        try {
            digest = MessageDigest.getInstance("SHA-256").digest(token.getBytes(StandardCharsets.UTF_8));
        } catch (java.security.NoSuchAlgorithmException ex) {
            throw new IllegalStateException("SHA-256 不可用", ex);
        }
        return Base64.getUrlEncoder().withoutPadding().encodeToString(digest);
    }

    private String rawBearerToken(String authorization) {
        if (authorization == null || !authorization.regionMatches(true, 0, BEARER_PREFIX, 0, BEARER_PREFIX.length())) {
            return null;
        }
        String token = authorization.substring(BEARER_PREFIX.length()).trim();
        return token.isEmpty() ? null : token;
    }
}
