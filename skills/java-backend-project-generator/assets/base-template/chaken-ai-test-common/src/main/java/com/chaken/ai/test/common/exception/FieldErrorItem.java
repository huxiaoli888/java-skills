package com.chaken.ai.test.common.exception;

public class FieldErrorItem {
    private String field;
    private String message;
    private String messageKey;
    private Object rejectedValue;

    public FieldErrorItem() {
    }

    public FieldErrorItem(String field, String message, String messageKey, Object rejectedValue) {
        this.field = field;
        this.message = message;
        this.messageKey = messageKey;
        this.rejectedValue = rejectedValue;
    }

    public String getField() {
        return field;
    }

    public void setField(String field) {
        this.field = field;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public String getMessageKey() {
        return messageKey;
    }

    public void setMessageKey(String messageKey) {
        this.messageKey = messageKey;
    }

    public Object getRejectedValue() {
        return rejectedValue;
    }

    public void setRejectedValue(Object rejectedValue) {
        this.rejectedValue = rejectedValue;
    }
}
