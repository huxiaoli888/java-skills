package com.chaken.ai.test.common.permission.aspect;

import com.chaken.ai.test.common.permission.annotation.RequirePermission;
import com.chaken.ai.test.common.permission.context.PrincipalContext;
import com.chaken.ai.test.common.permission.model.AuthenticatedPrincipal;
import com.chaken.ai.test.common.permission.service.PermissionEvaluator;
import com.chaken.ai.test.common.code.CommonErrorCode;
import com.chaken.ai.test.common.exception.BusinessException;
import java.lang.reflect.Method;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.reflect.MethodSignature;

@Aspect
public class PermissionAuthorizationAspect {
    private final PermissionEvaluator permissionEvaluator;

    public PermissionAuthorizationAspect(PermissionEvaluator permissionEvaluator) {
        this.permissionEvaluator = permissionEvaluator;
    }

    @Around("@within(com.chaken.ai.test.common.permission.annotation.RequirePermission) || @annotation(com.chaken.ai.test.common.permission.annotation.RequirePermission)")
    public Object authorize(ProceedingJoinPoint joinPoint) throws Throwable {
        RequirePermission required = findRequiredPermission(joinPoint);
        if (required == null) {
            return joinPoint.proceed();
        }
        AuthenticatedPrincipal principal = PrincipalContext.current()
                .orElseThrow(() -> new BusinessException(CommonErrorCode.UNAUTHORIZED));
        if (!permissionEvaluator.hasPermission(principal, required.value(), required.any())) {
            throw new BusinessException(CommonErrorCode.FORBIDDEN);
        }
        return joinPoint.proceed();
    }

    private RequirePermission findRequiredPermission(ProceedingJoinPoint joinPoint) {
        MethodSignature signature = (MethodSignature) joinPoint.getSignature();
        Method method = signature.getMethod();
        RequirePermission methodAnnotation = method.getAnnotation(RequirePermission.class);
        if (methodAnnotation != null) {
            return methodAnnotation;
        }
        Class<?> targetClass = joinPoint.getTarget() == null
                ? signature.getDeclaringType()
                : joinPoint.getTarget().getClass();
        return targetClass.getAnnotation(RequirePermission.class);
    }
}
