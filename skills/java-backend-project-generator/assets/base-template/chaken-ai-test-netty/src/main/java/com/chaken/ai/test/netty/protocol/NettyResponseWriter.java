package com.chaken.ai.test.netty.protocol;

import com.chaken.ai.test.common.api.ApiResult;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;
import org.springframework.stereotype.Component;

@Component
public class NettyResponseWriter {
    private final ObjectMapper objectMapper;

    public NettyResponseWriter(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    public String success(String reqid, Object data) {
        return toJson(ApiResult.success(data, reqidOrGenerated(reqid)));
    }

    public String fail(String reqid, String code, String message) {
        return toJson(ApiResult.fail(code, message, reqidOrGenerated(reqid)));
    }

    public String ack(String reqid, String ackFunc, String ackStatus, Long receivedSeqno) {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("ackFunc", ackFunc);
        data.put("ackStatus", ackStatus);
        if (receivedSeqno != null) {
            data.put("receivedSeqno", receivedSeqno);
        }
        return success(reqid, data);
    }

    private String toJson(ApiResult<?> result) {
        try {
            return objectMapper.writeValueAsString(result);
        } catch (JsonProcessingException ex) {
            throw new IllegalStateException("Netty response serialization failed", ex);
        }
    }

    private String reqidOrGenerated(String reqid) {
        if (reqid != null && !reqid.trim().isEmpty()) {
            return reqid;
        }
        return "server-" + UUID.randomUUID().toString();
    }
}
