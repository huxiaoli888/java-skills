package {{basePackage}}.lock;

import java.time.Duration;
import java.util.UUID;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

@Service
public class {{lockServiceClass}} {
    private final StringRedisTemplate redisTemplate;

    public {{lockServiceClass}}(StringRedisTemplate redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    public String tryLock(String key, Duration ttl) {
        String token = UUID.randomUUID().toString();
        Boolean locked = redisTemplate.opsForValue().setIfAbsent(key, token, ttl);
        return Boolean.TRUE.equals(locked) ? token : null;
    }

    public void unlock(String key, String token) {
        String current = redisTemplate.opsForValue().get(key);
        if (token != null && token.equals(current)) {
            redisTemplate.delete(key);
        }
    }
}
