package com.chaken.ai.test.common.log.annotation;

import com.chaken.ai.test.common.log.model.OperationType;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface OperationAudit {
    String action();

    OperationType type() default OperationType.OTHER;

    String businessId() default "";

    String detail() default "";
}
