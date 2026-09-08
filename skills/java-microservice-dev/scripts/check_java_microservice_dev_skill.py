#!/usr/bin/env python3
"""Validate the java-microservice-dev skill package."""

from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    errors: list[str] = []
    skill_text = read_text(ROOT / "SKILL.md")
    agents_text = read_text(ROOT / "agents" / "openai.yaml")
    response_template = read_text(ROOT / "templates" / "api-response.java")
    error_code_template = read_text(ROOT / "templates" / "error-code.java")
    common_error_code_template = read_text(ROOT / "templates" / "common-error-code.java")
    controller_template = read_text(ROOT / "templates" / "controller.java")
    exception_template = read_text(ROOT / "templates" / "global-exception-handler.java")
    service_template = read_text(ROOT / "templates" / "service.java")
    scenarios_path = ROOT / "references" / "forward-test-scenarios.md"
    runner_path = ROOT / "scripts" / "run_forward_tests.py"
    scenarios_text = read_text(scenarios_path) if scenarios_path.exists() else ""
    runner_text = read_text(runner_path) if runner_path.exists() else ""
    testing_guide_text = read_text(ROOT / "references" / "testing-guide.md")
    security_baseline_text = read_text(ROOT / "references" / "security-baseline.md")

    for needle in [
        "本技能负责具体 Spring Boot 业务实现，不制定全局标准",
        "## API 实现",
        "## Service 实现",
        "## 数据访问",
        "## 异常与错误映射",
        "## 测试策略",
        "## 输出契约",
        "reqid/code/message/ts/data",
        "java-backend-api-standard",
        "java-development-principles",
        "java-multi-module-architecture",
        "netty-handler-dispatcher",
        "默认模板以 Spring Boot 2.x + JDK8 为基线",
        "终端或 H5 必须为每次请求生成 `x-reqid`",
        "不要在服务端为 HTTP Controller 请求静默生成 reqid",
        "缺失其他必传请求头时仍应回显已存在的 `x-reqid`",
        "不得返回 `reqid: null`",
        "templates/error-code.java",
        "templates/common-error-code.java",
        "references/forward-test-scenarios.md",
        "scripts/run_forward_tests.py",
    ]:
        if needle not in skill_text:
            errors.append(f"SKILL.md 缺少微服务实现边界：{needle}")

    for needle in ["policy:", "trigger_keywords:", "Controller", "Service", "Mapper", "Redis", "MQ", "测试"]:
        if needle not in agents_text:
            errors.append(f"agents/openai.yaml 缺少触发关键词：{needle}")

    for needle in [
        "reqid",
        "code",
        "message",
        "data",
        "ts",
        "ErrorCode",
        "CommonErrorCode.SUCCESS",
        "reqidOrEmpty(String reqid)",
        "response.reqid = reqidOrEmpty(reqid)",
    ]:
        if needle not in response_template:
            errors.append(f"templates/api-response.java 缺少统一响应字段或成功码：{needle}")

    for forbidden in ['code = "0"', 'response.code = "000000"', "traceId", "status", "java.util.UUID", ".isBlank()"]:
        if forbidden in response_template:
            errors.append(f"templates/api-response.java 不应包含旧响应契约：{forbidden}")

    for needle in ["interface ErrorCode", "String code()", "String defaultMessage()", "int httpStatus()"]:
        if needle not in error_code_template:
            errors.append(f"templates/error-code.java 缺少中心化错误码接口定义：{needle}")

    for needle in ['SUCCESS("000000"', 'PARAM_INVALID("AC0001"', 'SYSTEM_ERROR("AC9999"', "implements ErrorCode"]:
        if needle not in common_error_code_template:
            errors.append(f"templates/common-error-code.java 缺少公共错误码枚举定义：{needle}")

    getter_order = [
        response_template.find("public String getReqid()"),
        response_template.find("public String getCode()"),
        response_template.find("public String getMessage()"),
        response_template.find("public long getTs()"),
        response_template.find("public T getData()"),
    ]
    if any(index < 0 for index in getter_order) or getter_order != sorted(getter_order):
        errors.append("templates/api-response.java getter 顺序必须匹配 reqid/code/message/ts/data")

    if "reqid/code/message/data/ts" in skill_text:
        errors.append("SKILL.md 不应继续使用旧响应字段顺序：reqid/code/message/data/ts")

    for needle in [
        "ApiResponse<{{responseClass}}>",
        '@RequestHeader(value = "x-reqid", required = true) String reqid',
        "ApiResponse.success(service.{{methodName}}(request), reqid)",
        "import javax.validation.Valid;",
    ]:
        if needle not in controller_template:
            errors.append(f"templates/controller.java 未使用统一响应模板或 reqid：{needle}")

    for forbidden in ['required = false', "jakarta.validation.Valid"]:
        if forbidden in controller_template:
            errors.append(f"templates/controller.java 不应放松 x-reqid 或硬编码 Spring Boot 3 包：{forbidden}")

    for needle in [
        "HttpServletRequest request",
        "import javax.validation.ConstraintViolationException;",
        "import javax.servlet.http.HttpServletRequest;",
        "MissingRequestHeaderException",
        'request.getHeader("x-reqid")',
        "CommonErrorCode.PARAM_INVALID",
        "CommonErrorCode.SYSTEM_ERROR",
        "import org.slf4j.Logger;",
        "import org.slf4j.LoggerFactory;",
        "private static final Logger log",
        'log.error("未预期异常 reqid={}"',
        "reqidOrEmpty(HttpServletRequest request)",
        "handleMissingRequestHeader(MissingRequestHeaderException ex, HttpServletRequest request)",
        "ApiResponse.error(CommonErrorCode.PARAM_INVALID, reqidOrEmpty(request))",
    ]:
        if needle not in exception_template:
            errors.append(f"templates/global-exception-handler.java 未使用统一错误码或 reqid：{needle}")

    for forbidden in [
        'ApiResponse.error("',
        'ApiResponse.error("VALIDATION_400"',
        'ApiResponse.error("INTERNAL_500"',
        'ApiResponse.error("AC0001", "Invalid request");',
        "ApiResponse.error(CommonErrorCode.PARAM_INVALID, null)",
        "handleMissingRequestHeader(MissingRequestHeaderException ex) {",
    ]:
        if forbidden in exception_template:
            errors.append(f"templates/global-exception-handler.java 存在硬编码或旧错误响应调用：{forbidden}")

    for forbidden in ["jakarta.validation", "jakarta.servlet"]:
        if forbidden in exception_template:
            errors.append(f"templates/global-exception-handler.java 不应硬编码 Spring Boot 3 包：{forbidden}")

    if "TODO" in service_template:
        errors.append("templates/service.java 不应保留 TODO 占位异常")

    for needle in ["# Java 微服务测试指南", "## 测试选择", "## 验证降级", "MockMvc 或 WebTestClient"]:
        if needle not in testing_guide_text:
            errors.append(f"references/testing-guide.md 缺少中文测试指南关键项：{needle}")

    for needle in ["# Java 微服务安全基线", "## 基线检查", "保留现有认证和授权层", "不记录 token"]:
        if needle not in security_baseline_text:
            errors.append(f"references/security-baseline.md 缺少中文安全基线关键项：{needle}")

    for relative, text in {
        "references/testing-guide.md": testing_guide_text,
        "references/security-baseline.md": security_baseline_text,
    }.items():
        for stale in ["Use this reference", "Test Selection", "Verification Fallback", "Baseline Checks"]:
            if stale in text:
                errors.append(f"{relative} 存在英文引用残留：{stale}")

    for needle in ["场景一：新增 POST 接口", "场景二：Boot2/JDK8 项目", "场景三：签名接口顺序", "### Expected Findings", "keyword:"]:
        if needle not in scenarios_text:
            errors.append(f"references/forward-test-scenarios.md 缺少微服务前向验证内容：{needle}")

    for needle in ["--score-output", "--score-fixtures", "FIXTURE_OUTPUT_DIR", "keyword:", "SKILL_NAME = ROOT.name"]:
        if needle not in runner_text:
            errors.append(f"scripts/run_forward_tests.py 缺少可评分 forward-test 能力：{needle}")

    if errors:
        print("java-microservice-dev 技能检查失败：")
        for error in errors:
            print(f"- {error}")
        return 1
    print("java-microservice-dev 技能检查通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
