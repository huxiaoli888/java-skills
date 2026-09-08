package {{basePackage}}.cache;

public final class {{redisKeyClass}} {
    private static final String PREFIX = "{{projectPrefix}}:";

    private {{redisKeyClass}}() {
    }

    public static String byBizId(String bizId) {
        return PREFIX + "biz:" + bizId;
    }
}
