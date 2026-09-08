package {{basePackage}}.exception;

public interface ErrorCode {

    String code();

    String defaultMessage();

    int httpStatus();
}
