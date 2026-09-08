package {{basePackage}}.cache;

import java.time.Duration;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

@Service
public class {{cacheServiceClass}} {
    private final StringRedisTemplate redisTemplate;

    public {{cacheServiceClass}}(StringRedisTemplate redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    public void put(String key, String value, Duration ttl) {
        redisTemplate.opsForValue().set(key, value, ttl);
    }

    public String get(String key) {
        return redisTemplate.opsForValue().get(key);
    }

    public void delete(String key) {
        redisTemplate.delete(key);
    }
}
