package com.chaken.ai.test.common.log.aspect;

import com.chaken.ai.test.common.log.annotation.OperationAudit;
import com.chaken.ai.test.common.log.model.OperationAuditRecord;
import com.chaken.ai.test.common.log.service.OperationAuditService;
import com.chaken.ai.test.common.trace.TraceContext;
import com.chaken.ai.test.security.signature.SignatureHeaders;
import jakarta.servlet.http.HttpServletRequest;
import java.time.Instant;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

@Aspect
@Component
public class OperationAuditAspect {
    private static final Logger log = LoggerFactory.getLogger(OperationAuditAspect.class);
    private final OperationAuditService operationAuditService;

    public OperationAuditAspect(OperationAuditService operationAuditService) {
        this.operationAuditService = operationAuditService;
    }

    @Around("@annotation(operationAudit)")
    public Object audit(ProceedingJoinPoint joinPoint, OperationAudit operationAudit) throws Throwable {
        long start = System.currentTimeMillis();
        boolean success = false;
        String errorMessage = null;
        try {
            Object result = joinPoint.proceed();
            success = true;
            return result;
        } catch (Throwable ex) {
            errorMessage = ex.getClass().getSimpleName();
            throw ex;
        } finally {
            OperationAuditRecord record = buildRecord(operationAudit, start, success, errorMessage);
            try {
                operationAuditService.save(record);
            } catch (RuntimeException auditEx) {
                log.error("operation audit save failed reqid={}", TraceContext.requestId(), auditEx);
            }
        }
    }

    private OperationAuditRecord buildRecord(
            OperationAudit operationAudit,
            long start,
            boolean success,
            String errorMessage) {
        HttpServletRequest request = currentRequest();
        OperationAuditRecord record = new OperationAuditRecord();
        record.setOperator(operator(request));
        record.setOperationType(operationAudit.type());
        record.setAction(operationAudit.action());
        record.setBusinessId(operationAudit.businessId());
        record.setDetail(operationAudit.detail());
        record.setSuccess(success);
        record.setErrorMessage(errorMessage);
        record.setTraceId(TraceContext.traceId());
        record.setReqid(TraceContext.requestId());
        record.setDurationMs(System.currentTimeMillis() - start);
        record.setTimestamp(Instant.now());
        if (request != null) {
            record.setHttpMethod(request.getMethod());
            record.setPath(request.getRequestURI());
            record.setClientIp(clientIp(request));
            record.setUserAgent(request.getHeader("user-agent"));
        }
        return record;
    }

    private HttpServletRequest currentRequest() {
        if (RequestContextHolder.getRequestAttributes() instanceof ServletRequestAttributes attributes) {
            return attributes.getRequest();
        }
        return null;
    }

    private String operator(HttpServletRequest request) {
        if (request == null) {
            return "";
        }
        Object adminId = request.getAttribute("adminId");
        if (adminId != null) {
            return String.valueOf(adminId);
        }
        String udid = request.getHeader(SignatureHeaders.UDID);
        return udid == null ? "" : udid;
    }

    private String clientIp(HttpServletRequest request) {
        String forwardedFor = request.getHeader("x-forwarded-for");
        if (forwardedFor != null && !forwardedFor.isBlank()) {
            return forwardedFor.split(",")[0].trim();
        }
        return request.getRemoteAddr();
    }
}
