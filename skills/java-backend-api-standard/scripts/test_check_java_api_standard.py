#!/usr/bin/env python3
"""Self-checks for check_java_api_standard.py.

The tests create tiny throwaway Java projects so the skill can validate checker
behavior without shipping bulky fixture projects.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


SCRIPT_DIR = Path(__file__).resolve().parent
CHECKER_PATH = SCRIPT_DIR / "check_java_api_standard.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_java_api_standard", CHECKER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载检查器：{CHECKER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    checker = load_checker()

    with tempfile.TemporaryDirectory(prefix="java-api-standard-baseentity-op-version-") as tmp:
        root = Path(tmp)
        write_text(
            root / "src/main/java/com/example/common/persistence/BaseEntity.java",
            """
package com.example.common.persistence;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.Version;

public abstract class BaseEntity {
    @TableField("op_version")
    @Version
    private Long opVersion;
}
""".strip(),
        )

        findings = checker.run(root, profile="minimal")
        messages = [finding.message for finding in findings]

        assert_true(
            any("op_version" in message and "version" in message for message in messages),
            "BaseEntity 使用 op_version/opVersion 时应提示改回 version",
        )

    with tempfile.TemporaryDirectory(prefix="java-api-standard-mybatis-plus-optimistic-") as tmp:
        root = Path(tmp)
        write_text(
            root / "src/main/java/com/example/cms/config/MybatisPlusConfiguration.java",
            """
package com.example.cms.config;

import com.baomidou.mybatisplus.extension.plugins.MybatisPlusInterceptor;
import com.baomidou.mybatisplus.extension.plugins.inner.BlockAttackInnerInterceptor;
import com.baomidou.mybatisplus.extension.plugins.inner.PaginationInnerInterceptor;

public class MybatisPlusConfiguration {
    public MybatisPlusInterceptor mybatisPlusInterceptor() {
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        interceptor.addInnerInterceptor(new PaginationInnerInterceptor());
        interceptor.addInnerInterceptor(new BlockAttackInnerInterceptor());
        return interceptor;
    }
}
""".strip(),
        )

        findings = checker.run(root, profile="minimal")
        messages = [finding.message for finding in findings]

        assert_true(
            any("OptimisticLockerInnerInterceptor" in message for message in messages),
            "MybatisPlusInterceptor 缺少 OptimisticLockerInnerInterceptor 时应触发检查",
        )

    with tempfile.TemporaryDirectory(prefix="java-api-standard-negative-") as tmp:
        root = Path(tmp)
        write_text(
            root / "src/main/java/com/example/security/SignatureHeaders.java",
            """
package com.example.security;

public final class SignatureHeaders {
    public static final String SIGNATURE_ALG = "x-signature-alg";
    public static final String NONCE = "x-nonce";
}
""".strip(),
        )

        findings = checker.run(root, profile="minimal")
        rules = {finding.rule for finding in findings}
        messages = [finding.message for finding in findings]

        assert_true(findings, "负样例应产生检查结果")
        assert_true(all("template" not in finding.rule for finding in findings), "规则 ID 不应继续使用 template 命名")
        assert_true("required-component" in rules, "缺失基础组件应使用 required-component 规则")
        assert_true("signature-header-contract" in rules, "废弃签名请求头应触发签名头契约检查")
        assert_true(any("x-signature-alg" in message for message in messages), "应提示 x-signature-alg 已废弃")
        assert_true(any("x-nonce" in message for message in messages), "应提示 x-nonce 已废弃")
        assert_true(all(" was not found" not in message for message in messages), "错误提示不应包含英文 was not found")

    with tempfile.TemporaryDirectory(prefix="java-api-standard-minimal-") as tmp:
        root = Path(tmp)
        write_text(root / "docs/development/version_compatibility.md", "当前脚手架已通过 common/cms-api/sdk-api 编译。")

        findings = checker.run(root, profile="minimal")
        rules = {finding.rule for finding in findings}

        assert_true("minimal-sdk-contract-residue" in rules, "minimal profile 应检查文档或脚本中的 sdk-api 残留")

    with tempfile.TemporaryDirectory(prefix="java-api-standard-signature-") as tmp:
        root = Path(tmp)
        write_text(
            root / "src/main/java/com/example/security/SignatureAuthenticationSupport.java",
            """
package com.example.security;

public class SignatureAuthenticationSupport {
    public void authenticate(Request request) {
        request.getHeader(SignatureHeaders.SIGN);
        request.getHeader(SignatureHeaders.REQID);
        RequestSigner.hmacSha256Base64("", "");
        RequestSigner.constantTimeEquals("", "");
        ReplayRequestStore store = null;
    }
}
""".strip(),
        )

        findings = checker.run(root, profile="minimal")
        messages = [finding.message for finding in findings]

        assert_true(
            any("x-sign-alg" in message and "x-api-version" in message for message in messages),
            "签名认证组件缺少 x-sign-alg/x-api-version 时应明确提示",
        )

    with tempfile.TemporaryDirectory(prefix="java-api-standard-replay-store-") as tmp:
        root = Path(tmp)
        write_text(
            root / "src/main/java/com/example/security/ReplayRequestStore.java",
            """
package com.example.security;

import java.time.Duration;

public interface ReplayRequestStore {
    boolean saveIfAbsent(String apiKey, String reqid, Duration ttl);
}
""".strip(),
        )

        findings = checker.run(root, profile="minimal")
        rules = {finding.rule for finding in findings}
        messages = [finding.message for finding in findings]

        assert_true("replay-component-contract" in rules, "ReplayRequestStore 旧 apiKey 参数名应触发 replay 组件契约检查")
        assert_true(any("replaySubject" in message for message in messages), "ReplayRequestStore 应提示改用 replaySubject")

    with tempfile.TemporaryDirectory(prefix="java-api-standard-signature-payload-") as tmp:
        root = Path(tmp)
        write_text(
            root / "src/main/java/com/example/security/SignatureCanonicalPayload.java",
            """
package com.example.security;

public class SignatureCanonicalPayload {
    public String canonicalUrlEncoded(String value) {
        return value;
    }
}
""".strip(),
        )

        findings = checker.run(root, profile="minimal")
        rules = {finding.rule for finding in findings}

        assert_true("signature-payload-contract" in rules, "签名 payload 规范化组件缺少 form/query 规则时应触发检查")

    with tempfile.TemporaryDirectory(prefix="java-api-standard-controller-") as tmp:
        root = Path(tmp)
        write_text(
            root / "src/main/java/com/example/cms/controller/SampleController.java",
            """
package com.example.cms.controller;

import com.example.cms.entity.SampleEntity;
import java.util.Map;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class SampleController {
    public Map<String, Object> list() {
        return Map.of("ok", true);
    }
}
""".strip(),
        )

        findings = checker.run(root, profile="minimal")
        rules = {finding.rule for finding in findings}

        assert_true("controller-raw-return" in rules, "Controller 原始返回类型应触发检查")
        assert_true("controller-entity-import" in rules, "Controller 导入 entity 应触发 DTO 边界检查")

    with tempfile.TemporaryDirectory(prefix="java-api-standard-complex-sql-") as tmp:
        root = Path(tmp)
        write_text(
            root / "src/main/java/com/example/order/mapper/OrderMapper.java",
            """
package com.example.order.mapper;

import org.apache.ibatis.annotations.Select;

public interface OrderMapper {
    @Select("select o.id, u.name from orders o join users u on o.user_id = u.id group by u.name")
    Object query();
}
""".strip(),
        )

        findings = checker.run(root, profile="minimal")
        rules = {finding.rule for finding in findings}

        assert_true("complex-sql-should-use-xml" in rules, "复杂 SQL 注解应提示改用 Mapper XML")

    with tempfile.TemporaryDirectory(prefix="java-api-standard-exception-") as tmp:
        root = Path(tmp)
        write_text(
            root / "src/main/java/com/example/security/SampleSecurityFilter.java",
            """
package com.example.security;

public class SampleSecurityFilter {
    public boolean expired(String value) {
        try {
            Long.parseLong(value);
            return false;
        } catch (RuntimeException ex) {
            return true;
        }
    }
}
""".strip(),
        )

        findings = checker.run(root, profile="minimal")
        rules = {finding.rule for finding in findings}

        assert_true("exception-swallowed" in rules, "catch 处理异常但没有 log.error 或 rethrow 时应触发检查")

    with tempfile.TemporaryDirectory(prefix="java-api-standard-expected-rejection-") as tmp:
        root = Path(tmp)
        write_text(
            root / "src/main/java/com/example/security/SdkSecurityFilter.java",
            """
package com.example.security;

public class SdkSecurityFilter {
    public void doFilter(Request request, Response response) {
        try {
            authenticate(request);
        } catch (SignatureAuthenticationException ex) {
            log.info("sdk_signature_auth_failed path={} code={}",
                    request.path(), ex.errorCode().code());
            SecurityErrorResponseWriter.write(response, ex.errorCode());
        }
    }
}
""".strip(),
        )

        findings = checker.run(root, profile="minimal")
        rules = {finding.rule for finding in findings}

        assert_true("exception-swallowed" not in rules, "可预期签名拒绝已写统一错误响应时不应误报吞异常")

    with tempfile.TemporaryDirectory(prefix="java-api-standard-netty-protocol-invalid-") as tmp:
        root = Path(tmp)
        write_text(
            root / "src/main/java/com/example/netty/tcp/NettyTcpMessageHandler.java",
            """
package com.example.netty.tcp;

import com.fasterxml.jackson.core.JsonProcessingException;

public class NettyTcpMessageHandler {
    public void handle(ChannelContext context, ResponseWriter responseWriter) {
        String reqid = "";
        try {
            parse();
        } catch (JsonProcessingException ex) {
            context.writeAndFlush(responseWriter.fail(reqid, "AC0001", "协议格式错误"));
            log.info("netty_tcp_protocol_invalid reqid={} code={}", reqid, "AC0001");
        }
    }
}
""".strip(),
        )

        findings = checker.run(root, profile="minimal")
        rules = {finding.rule for finding in findings}

        assert_true("exception-swallowed" not in rules, "可预期 Netty 协议格式错误已返回统一响应并 info 记录时不应误报吞异常")

    with tempfile.TemporaryDirectory(prefix="java-api-standard-netty-custom-protocol-invalid-") as tmp:
        root = Path(tmp)
        write_text(
            root / "src/main/java/com/example/netty/tcp/NettyTcpMessageHandler.java",
            """
package com.example.netty.tcp;

public class NettyTcpMessageHandler {
    public void handle(ChannelContext context, ResponseWriter responseWriter) {
        String reqid = "";
        try {
            decode();
        } catch (ProtocolDecodeException ex) {
            log.info("netty_tcp_protocol_invalid reqid={} code={}", reqid, "AC0001");
            context.writeAndFlush(responseWriter.fail(reqid, "AC0001", "协议格式错误"));
        }
    }
}

class ProtocolDecodeException extends Exception {
}
""".strip(),
        )

        findings = checker.run(root, profile="minimal")
        rules = {finding.rule for finding in findings}

        assert_true("exception-swallowed" not in rules, "自定义协议格式错误异常已返回统一响应并 info 记录时不应误报吞异常")

    with tempfile.TemporaryDirectory(prefix="java-api-standard-business-exception-flow-") as tmp:
        root = Path(tmp)
        write_text(
            root / "src/main/java/com/example/order/service/OrderService.java",
            """
package com.example.order.service;

import com.example.common.exception.BusinessException;
import com.example.common.code.CommonErrorCode;

public class OrderService {
    public Object getOrder(String orderNo) {
        if (orderNo == null) {
            throw new BusinessException(CommonErrorCode.RESOURCE_NOT_FOUND);
        }
        return new Object();
    }
}
""".strip(),
        )

        findings = checker.run(root, profile="minimal")
        rules = {finding.rule for finding in findings}

        assert_true(
            "business-exception-control-flow" in rules,
            "service/domain/application 层把业务失败写成 BusinessException 控制流时应触发检查",
        )

    with tempfile.TemporaryDirectory(prefix="java-api-standard-error-code-package-") as tmp:
        root = Path(tmp)
        write_text(
            root / "src/main/java/com/example/common/error/CommonErrorCode.java",
            """
package com.example.common.error;

public enum CommonErrorCode implements ErrorCode {
    SUCCESS("000000", "common.success", "成功");

    private final String code;
    private final String messageKey;
    private final String defaultMessage;

    CommonErrorCode(String code, String messageKey, String defaultMessage) {
        this.code = code;
        this.messageKey = messageKey;
        this.defaultMessage = defaultMessage;
    }

    public String code() {
        return code;
    }
}
""".strip(),
        )

        findings = checker.run(root, profile="minimal")
        rules = {finding.rule for finding in findings}
        messages = [finding.message for finding in findings]

        assert_true("error-code-package-contract" in rules, "错误码继续放在 common.error 时应触发包名契约检查")
        assert_true(any("common.code" in message for message in messages), "错误提示应明确建议使用 common.code")

    with tempfile.TemporaryDirectory(prefix="java-api-standard-error-code-format-") as tmp:
        root = Path(tmp)
        write_text(
            root / "src/main/java/com/example/common/code/CommonErrorCode.java",
            """
package com.example.common.code;

public enum CommonErrorCode implements ErrorCode {
    SUCCESS("000000", "success"),
    PARAM_INVALID("AC0001", "bad request"),
    LEGACY_NUMERIC("100001", "legacy numeric"),
    TOO_SHORT("A0001", "too short"),
    LOWER_CASE("ac0002", "lowercase");

    private final String code;
    private final String message;

    CommonErrorCode(String code, String message) {
        this.code = code;
        this.message = message;
    }

    public String code() {
        return code;
    }
}
""".strip(),
        )

        findings = checker.run(root, profile="minimal")
        rules = {finding.rule for finding in findings}
        messages = [finding.message for finding in findings]

        assert_true("error-code-format" in rules, "错误码不满足 2 字母 + 4 数字格式时应触发检查")
        assert_true(any("100001" in message for message in messages), "纯数字失败码应被明确提示")
        assert_true(any("A0001" in message for message in messages), "长度不足的错误码应被明确提示")
        assert_true(any("ac0002" in message for message in messages), "小写错误码应被明确提示")

    with tempfile.TemporaryDirectory(prefix="java-api-standard-error-code-http-status-") as tmp:
        root = Path(tmp)
        write_text(
            root / "src/main/java/com/example/common/code/ErrorCode.java",
            """
package com.example.common.code;

public interface ErrorCode {
    String code();
    String messageKey();
    String defaultMessage();
    int httpStatus();
}
""".strip(),
        )
        write_text(
            root / "src/main/java/com/example/common/code/CommonErrorCode.java",
            """
package com.example.common.code;

public enum CommonErrorCode implements ErrorCode {
    SUCCESS("000000", "common.success", "成功", 200),
    PARAM_INVALID("AC0001", "common.param.invalid", "请求参数不合法", 400);

    private final String code;
    private final String messageKey;
    private final String defaultMessage;
    private final int httpStatus;

    CommonErrorCode(String code, String messageKey, String defaultMessage, int httpStatus) {
        this.code = code;
        this.messageKey = messageKey;
        this.defaultMessage = defaultMessage;
        this.httpStatus = httpStatus;
    }

    public String code() {
        return code;
    }

    public String messageKey() {
        return messageKey;
    }

    public String defaultMessage() {
        return defaultMessage;
    }

    public int httpStatus() {
        return httpStatus;
    }
}
""".strip(),
        )

        findings = checker.run(root, profile="minimal")
        rules = {finding.rule for finding in findings}
        messages = [finding.message for finding in findings]

        assert_true("error-code-contract" in rules, "ErrorCode 暴露 httpStatus 时应触发契约检查")
        assert_true("common-error-code-contract" in rules, "CommonErrorCode 携带 httpStatus 时应触发契约检查")
        assert_true(any("httpStatus" in message and "不要" in message for message in messages), "错误提示应明确不要在错误码契约中携带 httpStatus")

    with tempfile.TemporaryDirectory(prefix="java-api-standard-api-result-reqid-null-") as tmp:
        root = Path(tmp)
        write_text(
            root / "src/main/java/com/example/common/api/ApiResult.java",
            """
package com.example.common.api;

public class ApiResult<T> {
    private String reqid;
    private String code;
    private String message;
    private long ts;
    private T data;

    private ApiResult(String reqid, String code, String message, T data) {
        this.reqid = reqid;
        this.code = code;
        this.message = message;
        this.data = data;
    }

    public static <T> ApiResult<T> success(T data, String reqid) {
        return new ApiResult<>(reqid, "000000", "成功", data);
    }
}
""".strip(),
        )

        findings = checker.run(root, profile="minimal")
        rules = {finding.rule for finding in findings}

        assert_true("api-result-reqid-null-normalization" in rules, "ApiResult 原样保存 reqid 时应触发 null 归一化检查")

    with tempfile.TemporaryDirectory(prefix="java-api-standard-header-contract-") as tmp:
        root = Path(tmp)
        write_text(
            root / "src/main/resources/application.yml",
            """
api:
  cors:
    allowed-headers:
      - authorization
      - x-reqid
      - x-sign
""".strip(),
        )
        write_text(root / "docs/api/api_inventory.md", "接口请求头包含 authorization、x-reqid、x-sign。")
        write_text(root / "docs/development/security.md", "旧版请求头 x-nonce 不再使用。")

        findings = checker.run(root, profile="standard")
        rules = {finding.rule for finding in findings}
        messages = [finding.message for finding in findings]

        assert_true("shared-header-contract" in rules, "CORS 和文档请求头漂移应触发共享契约检查")
        assert_true(any("x-sign-alg" in message for message in messages), "缺少 x-sign-alg 应被共享契约检查提示")
        assert_true(any("x-api-version" in message for message in messages), "缺少 x-api-version 应被共享契约检查提示")
        assert_true(any("x-nonce" in message for message in messages), "文档残留 x-nonce 应被共享契约检查提示")

    with tempfile.TemporaryDirectory(prefix="java-api-standard-server-reqid-") as tmp:
        root = Path(tmp)
        write_text(
            root / "src/main/java/com/example/common/trace/RequestTraceLogFilter.java",
            """
package com.example.common.trace;

import java.util.UUID;

public class RequestTraceLogFilter {
    public static final String TRACE_ID_HEADER = "x-trace-id";
    public static final String REQUEST_ID_HEADER = "x-reqid";

    public void doFilter(Request request) {
        String traceId = firstNonBlank(request.getHeader(TRACE_ID_HEADER), UUID.randomUUID().toString());
        String requestId = firstNonBlank(request.getHeader(REQUEST_ID_HEADER), UUID.randomUUID().toString());
        TraceContext.put(traceId, requestId);
    }
}
""".strip(),
        )

        findings = checker.run(root, profile="minimal")
        rules = {finding.rule for finding in findings}

        assert_true("server-generated-reqid" in rules, "HTTP 服务端静默生成 x-reqid 时应触发检查")

    with tempfile.TemporaryDirectory(prefix="java-api-standard-traceid-ok-") as tmp:
        root = Path(tmp)
        write_text(
            root / "src/main/java/com/example/common/trace/RequestTraceLogFilter.java",
            """
package com.example.common.trace;

import java.util.UUID;

public class RequestTraceLogFilter {
    public static final String TRACE_ID_HEADER = "x-trace-id";
    public static final String REQUEST_ID_HEADER = "x-reqid";

    public void doFilter(Request request) {
        String traceId = firstNonBlank(request.getHeader(TRACE_ID_HEADER), UUID.randomUUID().toString());
        String requestId = request.getHeader(REQUEST_ID_HEADER);
        TraceContext.put(traceId, requestId);
    }
}
""".strip(),
        )

        findings = checker.run(root, profile="minimal")
        rules = {finding.rule for finding in findings}

        assert_true("server-generated-reqid" not in rules, "允许服务端生成 traceId，但不应误报为生成 x-reqid")

    with tempfile.TemporaryDirectory(prefix="java-api-standard-server-reqid-helper-") as tmp:
        root = Path(tmp)
        write_text(
            root / "src/main/java/com/example/common/trace/RequestTraceLogFilter.java",
            """
package com.example.common.trace;

import java.util.UUID;

public class RequestTraceLogFilter {
    public static final String REQUEST_ID_HEADER = "x-reqid";

    public void doFilter(Request request) {
        String requestId = firstNonBlank(request.getHeader(REQUEST_ID_HEADER), newId());
        TraceContext.put("trace", requestId);
    }

    private String newId() {
        return UUID.randomUUID().toString();
    }
}
""".strip(),
        )

        findings = checker.run(root, profile="minimal")
        rules = {finding.rule for finding in findings}

        assert_true("server-generated-reqid" in rules, "HTTP 服务端通过 helper 间接生成 x-reqid 时也应触发检查")

    with tempfile.TemporaryDirectory(prefix="java-api-standard-netty-") as tmp:
        root = Path(tmp)
        write_text(
            root / "demo-netty/src/main/resources/application.yml",
            """
server:
  port: 18082
management:
  endpoints:
    web:
      exposure:
        include: health
""".strip(),
        )

        findings = checker.run(root, profile="minimal")
        rules = {finding.rule for finding in findings}
        messages = [finding.message for finding in findings]

        assert_true("netty-module-component-missing" in rules, "Netty 模块缺少 dispatcher/auth/heartbeat/tcp/udp 时应触发检查")
        assert_true("netty-module-config-missing" in rules, "Netty 模块缺少 chaken.netty 配置时应触发检查")
        assert_true(any("chaken:" in message for message in messages), "Netty 配置缺少 chaken 根配置时应明确提示")

    generator_template = SCRIPT_DIR.parent.parent / "java-backend-project-generator" / "assets" / "base-template"
    assert_true(generator_template.exists(), f"生成器 base-template 不存在：{generator_template}")
    findings = checker.run(generator_template, profile="standard")
    assert_true(not findings, f"生成器 base-template standard profile 应通过检查：{findings}")

    completed = subprocess.run(
        [sys.executable, str(CHECKER_PATH), str(generator_template), "--profile", "production-ready"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert_true(completed.returncode == 2, "production-ready 不应再作为 checker profile 被接受")
    assert_true("invalid choice" in completed.stderr, "production-ready 应由 argparse choices 拒绝")

    print("通过：check_java_api_standard.py 自测全部通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
