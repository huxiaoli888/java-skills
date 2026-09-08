from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from netty_skill_rules import cluster_routing, global_contracts, implementation, observability, package_structure, protocol_format, response_contract, security
from netty_skill_rules.markdown import (
    validate_markdown_fences,
    validate_no_unresolved_placeholders,
    validate_toc_anchors,
)
from netty_skill_rules.templates import validate_templates_doc


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_RULES_PATH = ROOT / "references" / "contract-rules.json"

REQUIRED_REFERENCES = [
    "protocol-format.md",
    "netty-websocket.md",
    "netty-tcp-udp.md",
    "cluster-routing.md",
    "observability-testing.md",
    "templates.md",
    "signature-canonicalization.md",
    "response-contract.md",
    "implementation-plan.md",
    "implementation-layout.md",
    "forward-test-scenarios.md",
]

TEMPLATE_REFERENCE_FILES = [
    "design-review-template.md",
    "adr-template.md",
    "protocol-spec-template.md",
    "cluster-routing-template.md",
    "load-test-report-template.md",
]


def load_contract_rules() -> dict[str, list[str]]:
    if not CONTRACT_RULES_PATH.exists():
        raise FileNotFoundError(f"缺少契约规则数据文件：{CONTRACT_RULES_PATH}")
    data = json.loads(CONTRACT_RULES_PATH.read_text(encoding="utf-8"))
    rules: dict[str, list[str]] = {}
    for key, value in data.items():
        value = data.get(key)
        if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
            raise ValueError(f"contract-rules.json 的 {key} 必须是非空字符串数组")
        rules[key] = value
    for key in ["requiredText", "replayKeyText"]:
        if key not in rules:
            raise ValueError(f"contract-rules.json 缺少必需字段：{key}")
    return rules


CONTRACT_RULES = load_contract_rules()
REQUIRED_TEXT = CONTRACT_RULES["requiredText"]
REPLAY_KEY_TEXT = CONTRACT_RULES["replayKeyText"]
TEMPLATE_HTTP_REST_TEXT = CONTRACT_RULES["templateHttpRestText"]
TEMPLATE_RULE_TEXT_GROUPS = {
    key: CONTRACT_RULES[key]
    for key in [
        "templateMaintenanceBoundaryText",
        "templateConfigParameterText",
        "templateResponseAckBoundaryText",
        "templateResponseFooterText",
        "templateTcpUdpFieldText",
        "templateTcpUdpAnonymousText",
        "templateDevicePingLineText",
        "templatePublicPingLineText",
        "templateSignatureCostMetricText",
        "templateClusterConnectionBoundaryText",
        "templateClusterRouteFlowText",
        "templateClusterCleanupText",
        "templateClusterOpsRecoveryText",
        "templateClusterSequenceBoundaryText",
        "templateClusterNotificationMetricText",
        "templateLoadReportMetricText",
    ]
}
WEBSOCKET_HTTP_REST_BOUNDARY_TEXT = CONTRACT_RULES["websocketHttpRestBoundaryText"]
IMPLEMENTATION_HTTP_HEADER_TEXT = CONTRACT_RULES["implementationHttpHeaderText"]
IMPLEMENTATION_SIGNATURE_VERIFIER_TEXT = CONTRACT_RULES["implementationSignatureVerifierText"]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def add_error(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_forward_runner(errors: list[str]) -> None:
    runner = ROOT / "scripts" / "run_forward_tests.py"
    fixture_dir = ROOT / "references" / "forward-test-fixtures"
    if not runner.exists():
        add_error(errors, "缺少 forward-test runner：scripts/run_forward_tests.py")
        return
    runner_text = read_text(runner)
    for needle in ["--score-output", "--score-dir", "--score-fixtures", "FIXTURE_OUTPUT_DIR"]:
        if needle not in runner_text:
            add_error(errors, f"scripts/run_forward_tests.py 缺少按场景 fixture 评分能力：{needle}")
    if "FIXTURE_OUTPUT_FILE" in runner_text:
        add_error(errors, "scripts/run_forward_tests.py 的 --score-fixtures 不应继续使用合并 expected-output.md 评分")
    if (fixture_dir / "expected-output.md").exists():
        add_error(errors, "references/forward-test-fixtures/expected-output.md 已废弃，应使用 scenario-N.md")
    for index in range(1, 4):
        if not (fixture_dir / f"scenario-{index}.md").exists():
            add_error(errors, f"缺少按场景 forward-test fixture：references/forward-test-fixtures/scenario-{index}.md")


def validate_skill_frontmatter(text: str, errors: list[str]) -> str:
    return package_structure.validate_skill_frontmatter(text, errors)


def validate_skill_tree(errors: list[str]) -> None:
    package_structure.validate_skill_tree(ROOT, errors)


def validate_agents_file(errors: list[str]) -> None:
    package_structure.validate_agents_file(ROOT, read_text, errors)



def load_required_references(references_dir: Path, skill_text: str, errors: list[str]) -> tuple[dict[str, str], str]:
    """读取并验证登记的 reference 文件，避免 main() 承担目录装载细节。"""
    reference_texts: dict[str, str] = {}
    all_reference_markdown = ""
    actual_references = sorted(path.name for path in references_dir.glob("*.md")) if references_dir.exists() else []
    expected_references = sorted(REQUIRED_REFERENCES)
    for name in sorted(set(actual_references) - set(expected_references)):
        add_error(errors, f"references/ 存在未登记引用文件：{name}；请加入 REQUIRED_REFERENCES 并在 SKILL.md 导航中说明何时读取")
    for name in sorted(set(expected_references) - set(actual_references)):
        add_error(errors, f"REQUIRED_REFERENCES 登记了不存在的引用文件：{name}")
    if skill_text:
        for name in REQUIRED_REFERENCES:
            if f"references/{name}" not in skill_text:
                add_error(errors, f"SKILL.md 未导航引用文件：references/{name}")
    for name in REQUIRED_REFERENCES:
        ref = references_dir / name
        if not ref.exists():
            add_error(errors, f"缺少引用文件：{name}")
            continue
        ref_text = read_text(ref)
        reference_texts[name] = ref_text
        all_reference_markdown += "\n" + ref_text
        if len(ref_text.splitlines()) > 100 and "## 目录" not in "\n".join(ref_text.splitlines()[:30]):
            add_error(errors, f"长引用文件顶部必须包含目录：{name}")
        validate_markdown_fences(name, ref_text, errors)
        validate_no_unresolved_placeholders(name, ref_text, errors)
        validate_toc_anchors(name, ref_text, errors)
    return reference_texts, all_reference_markdown


def load_template_references(references_dir: Path, errors: list[str]) -> tuple[str, str]:
    """读取 templates.md 索引和模板子文件，保持模板拆分后仍按一个交付模板集合校验。"""
    templates_dir = references_dir / "templates"
    if not templates_dir.is_dir():
        add_error(errors, "缺少 references/templates/ 模板子目录")
        return "", ""
    actual_files = sorted(path.name for path in templates_dir.glob("*.md"))
    expected_files = sorted(TEMPLATE_REFERENCE_FILES)
    for name in sorted(set(actual_files) - set(expected_files)):
        add_error(errors, f"references/templates/ 存在未登记模板文件：{name}")
    for name in sorted(set(expected_files) - set(actual_files)):
        add_error(errors, f"references/templates/ 缺少模板文件：{name}")

    index_text = read_text(references_dir / "templates.md") if (references_dir / "templates.md").exists() else ""
    bundle_parts = [index_text]
    all_markdown = "\n" + index_text
    for name in TEMPLATE_REFERENCE_FILES:
        path = templates_dir / name
        if not path.exists():
            continue
        text = read_text(path)
        validate_markdown_fences(f"references/templates/{name}", text, errors)
        bundle_parts.append(text)
        all_markdown += "\n" + text
        if f"references/templates/{name}" not in index_text:
            add_error(errors, f"templates.md 模板索引未引用：references/templates/{name}")
    return "\n".join(bundle_parts), all_markdown


def validate_protocol_response_boundary_doc(protocol_text: str, errors: list[str]) -> None:
    response_contract.validate_protocol_response_boundary_doc(protocol_text, errors)


def validate_protocol_format_doc(protocol_text: str, errors: list[str]) -> None:
    protocol_format.validate_protocol_format_doc(protocol_text, errors)

def validate_protocol_signature_replay_doc(protocol_text: str, errors: list[str]) -> None:
    security.validate_protocol_signature_replay_doc(protocol_text, errors)



def validate_tcp_udp_doc(tcp_udp_text: str, errors: list[str]) -> None:
    security.validate_tcp_udp_doc(tcp_udp_text, errors)



def validate_signature_canonicalization_doc(signature_text: str, errors: list[str]) -> None:
    security.validate_signature_canonicalization_doc(signature_text, errors, REPLAY_KEY_TEXT)



def validate_signature_builder_boundaries_doc(signature_text: str, errors: list[str]) -> None:
    security.validate_signature_builder_boundaries_doc(signature_text, errors)



def validate_websocket_doc(websocket_text: str, errors: list[str]) -> None:
    security.validate_websocket_doc(websocket_text, errors, WEBSOCKET_HTTP_REST_BOUNDARY_TEXT)



def validate_cluster_routing_doc(cluster_text: str, errors: list[str]) -> None:
    cluster_routing.validate_cluster_routing_doc(cluster_text, errors)




def validate_skill_markdown_doc(skill_text: str, frontmatter: str, errors: list[str]) -> None:
    if "name: netty-handler-dispatcher" not in skill_text:
        add_error(errors, "SKILL.md frontmatter 必须使用 netty-handler-dispatcher")
    if "# Netty Handler Dispatcher" not in skill_text:
        add_error(errors, "SKILL.md 标题必须使用 Dispatcher")
    if "## 何时使用" in skill_text:
        add_error(errors, "SKILL.md 正文不应保留“何时使用”触发段，触发条件必须主要放在 frontmatter description")
    for text in ["Socket", "私有协议", "令牌上传/下载", "心跳", "ACK", "推送", "状态同步", "event loop 阻塞风险"]:
        if text not in frontmatter:
            add_error(errors, f"SKILL.md frontmatter description 必须覆盖触发语义：{text}")
    if "## 任务识别" not in skill_text:
        add_error(errors, "SKILL.md 正文应使用“任务识别”指导加载后的执行模式选择")
    for text in [
        "不要按每种动作创建一个连接或端口",
        "UDP 上层 route 必须短 TTL",
        "UDP datagram、TCP/WebSocket 连接接收、连接生命周期或 UDP route TTL",
        "每个业务动作创建一个 WebSocket/TCP 连接或 UDP 端口",
        "UDP route 短 TTL 和限流",
        "不按每个动作拆连接或端口",
        "UDP 有 route 短 TTL、限流和过期清理策略",
        "连接映射或 UDP route 映射",
    ]:
        if text not in skill_text:
            add_error(errors, f"SKILL.md 必须区分 TCP/WebSocket 连接与 UDP datagram/route：{text}")
    for text in [
        "不要按每种动作创建一个连接；",
        "| Transport | UDP/TCP/WebSocket 接收、连接生命周期、基础限流 |",
        "每个业务动作创建一个 WebSocket 连接。",
        "没有连接鉴权窗口、心跳超时和关闭码。",
        "入口按业务域聚合，不按每个动作拆连接。",
        "有心跳、鉴权、限流、超时和连接关闭策略。",
        "多实例场景有连接映射、跨节点通知、节点下线和滚动发布策略。",
    ]:
        if text in skill_text:
            add_error(errors, f"SKILL.md 仍存在会把 UDP 误导成连接协议的旧表述：{text}")
    if "Netty UDP、Netty TCP、Netty WebSocket 长连接协议入口" in skill_text:
        add_error(errors, "SKILL.md frontmatter 不应把 UDP/TCP/WebSocket 整体描述为长连接协议入口")
    if "Netty UDP/TCP/WebSocket 协议入口、TCP/WebSocket 长连接治理" not in skill_text:
        add_error(errors, "SKILL.md frontmatter 必须区分 UDP 协议入口与 TCP/WebSocket 长连接治理")
    for text in [
        "响应体不返回 `func/version/traceId/status`",
        "在响应 JSON 中返回 `func/version/traceId/status`",
        "响应 JSON 遵循 `reqid/code/message/ts/data`，且不包含 `func/version/traceId/status`",
    ]:
        if text not in skill_text:
            add_error(errors, f"SKILL.md 必须统一响应禁用字段口径：{text}")
    implementation_nav = next((line for line in skill_text.splitlines() if "做代码实现计划" in line), "")
    for text in ["signature-canonicalization.md", "cluster-routing.md", "response-contract.md"]:
        if text not in implementation_nav:
            add_error(errors, f"SKILL.md 的实现计划导航必须按条件提示读取：{text}")
    protocol_doc_nav = next((line for line in skill_text.splitlines() if "生成协议文档" in line), "")
    for text in ["netty-tcp-udp.md", "signature-canonicalization.md", "response-contract.md"]:
        if text not in protocol_doc_nav:
            add_error(errors, f"SKILL.md 的协议文档导航必须按条件提示读取：{text}")
    signature_nav = next((line for line in skill_text.splitlines() if "签名/防篡改" in line), "")
    for text in ["HTTP/REST", "signature-canonicalization.md"]:
        if text not in signature_nav:
            add_error(errors, f"SKILL.md 的签名导航必须覆盖 HTTP/REST 签名：{text}")
    signature_reference_line = next((line for line in skill_text.splitlines() if "references/signature-canonicalization.md" in line and "签名原文" in line), "")
    for text in ["HTTP/REST", "GET/POST JSON/CMS 表单 body hash", "query 排序"]:
        if text not in signature_reference_line:
            add_error(errors, f"SKILL.md 的 signature-canonicalization 引用说明必须覆盖 HTTP/REST body/query 规则：{text}")
    for text in [
        "## 规则归属与更新顺序",
        "先修改 source reference",
        "`response-contract.md` 是 Netty 响应 JSON、ACK、envelope 响应边界和协议错误映射的唯一归属",
        "`signature-canonicalization.md` 是签名原文、防重放、body hash、query 排序和 canonical builder 边界唯一归属",
        "`implementation-plan.md` 和 `implementation-layout.md` 只承载落地计划和代码结构",
        "`templates.md` 只承载交付模板",
        "最后更新并运行 `scripts/check_netty_handler_dispatcher_skill.py`",
    ]:
        if text not in skill_text:
            add_error(errors, f"SKILL.md 必须说明规则归属与更新顺序：{text}")
    performance_nav = next((line for line in skill_text.splitlines() if "评估性能或压测" in line), "")
    for text in ["observability-testing.md", "netty-websocket.md", "netty-tcp-udp.md"]:
        if text not in performance_nav:
            add_error(errors, f"SKILL.md 的性能压测导航必须按传输类型提示读取：{text}")
    validate_skill_self_check_section(skill_text, errors)
    if "ACK + V1" in skill_text or "AckHandler" in skill_text:
        add_error(errors, "SKILL.md 不应把 ACK 当作 func + version handler 注册示例")
    if "TOKEN_STATUS_NOTIFY + V1" in skill_text or "TokenStatusNotifyHandler" in skill_text:
        add_error(errors, "SKILL.md 不应把服务端通知 TOKEN_STATUS_NOTIFY 当作入站 handler 注册示例")
    if "DEVICE_STATUS_REPORT + V1 -> DeviceStatusReportHandler" not in skill_text:
        add_error(errors, "SKILL.md 的 handler 示例必须包含真实入站业务 DEVICE_STATUS_REPORT")


def validate_skill_self_check_section(skill_text: str, errors: list[str]) -> None:
    self_check_match = re.search(r"## 自检脚本(?P<body>[\s\S]*?)(?:\n## |\Z)", skill_text)
    self_check_text = self_check_match.group("body") if self_check_match else ""
    for text in ["UDID", "KEY_ID", "SIGN_ALG"]:
        if text not in self_check_text:
            add_error(errors, f"SKILL.md 的自检覆盖说明必须包含签名字段：{text}")
    for text in ["canonical builder", "`SignatureVerifier` 不构造 canonical string", "HTTP/REST GET/POST JSON/CMS 表单 query/body hash 来源"]:
        if text not in self_check_text:
            add_error(errors, f"SKILL.md 的自检覆盖说明必须包含签名构造边界：{text}")
    for text in ["WebSocket 高风险业务消息", "`sign/sign-alg/api-key`", "ws-message:{api-key}:{reqid}:{authSubject|connectionId}"]:
        if text not in self_check_text:
            add_error(errors, f"SKILL.md 的自检覆盖说明必须包含 WebSocket 高风险消息级签名和防重放边界：{text}")
    for text in ["高风险或已识别设备请求使用 `udid/sign/sign-alg/api-key`", "匿名公开探测可省略 `udid` 和签名材料"]:
        if text not in self_check_text:
            add_error(errors, f"SKILL.md 的自检覆盖说明必须包含匿名公开探测边界：{text}")
    for text in [
        "配置参数",
        "`websocket.auth-timeout-ms`",
        "`websocket.max-frame-payload-length`",
        "`security.timestamp-skew-seconds/security.replay-ttl-seconds`",
        "`tcp.max-frame-bytes`",
        "`udp.max-datagram-bytes`",
        "`udp.route-ttl-seconds`",
        "`rate-limit.max-qps-per-udid`",
    ]:
        if text not in self_check_text:
            add_error(errors, f"SKILL.md 的自检覆盖说明必须包含配置参数边界：{text}")
    for text in ["首条 `AUTH` 示例", "`handler/`", "publisher/writer", "错误拼写旧目录"]:
        if text not in self_check_text:
            add_error(errors, f"SKILL.md 的自检覆盖说明必须包含：{text}")


def validate_implementation_plan_doc(implementation_text: str, errors: list[str]) -> None:
    implementation.validate_implementation_plan_doc(
        implementation_text,
        errors,
        REPLAY_KEY_TEXT,
        IMPLEMENTATION_HTTP_HEADER_TEXT,
        IMPLEMENTATION_SIGNATURE_VERIFIER_TEXT,
    )




def validate_implementation_layout_doc(layout_text: str, errors: list[str]) -> None:
    implementation.validate_implementation_layout_doc(layout_text, errors, REPLAY_KEY_TEXT)




def validate_observability_testing_doc(observability_text: str, errors: list[str]) -> None:
    observability.validate_observability_testing_doc(observability_text, errors)





def validate_response_contract_doc(response_text: str, errors: list[str]) -> None:
    response_contract.validate_response_contract_doc(response_text, errors)



def main() -> int:
    errors: list[str] = []
    all_markdown = ""
    skill_text = ""
    global_contracts.validate_internal_sanity(errors)
    validate_skill_tree(errors)
    validate_forward_runner(errors)

    legacy_skill_dirs = [
        ROOT.parent / "udp-websocket-handler-dispather",
        ROOT.parent / "netty-handler-dispather",
    ]
    for legacy_dir in legacy_skill_dirs:
        if legacy_dir.exists():
            add_error(errors, f"skills 根目录仍存在错误拼写旧目录：{legacy_dir.name}")

    skill_md = ROOT / "SKILL.md"
    if not skill_md.exists():
        add_error(errors, "缺少 SKILL.md")
    else:
        skill_text = read_text(skill_md)
        all_markdown += "\n" + skill_text
        validate_markdown_fences("SKILL.md", skill_text, errors)
        frontmatter = validate_skill_frontmatter(skill_text, errors)
        validate_skill_markdown_doc(skill_text, frontmatter, errors)

    references_dir = ROOT / "references"
    reference_texts, reference_markdown = load_required_references(references_dir, skill_text, errors)
    all_markdown += reference_markdown
    templates_bundle_text, templates_markdown = load_template_references(references_dir, errors)
    all_markdown += templates_markdown

    global_contracts.validate_all_markdown_contracts(all_markdown, errors, REQUIRED_TEXT)

    validate_protocol_format_doc(reference_texts.get("protocol-format.md", ""), errors)

    validate_tcp_udp_doc(reference_texts.get("netty-tcp-udp.md", ""), errors)

    validate_signature_canonicalization_doc(reference_texts.get("signature-canonicalization.md", ""), errors)

    validate_websocket_doc(reference_texts.get("netty-websocket.md", ""), errors)

    validate_cluster_routing_doc(reference_texts.get("cluster-routing.md", ""), errors)

    validate_agents_file(errors)

    validate_templates_doc(templates_bundle_text, errors, TEMPLATE_HTTP_REST_TEXT, TEMPLATE_RULE_TEXT_GROUPS)

    validate_implementation_plan_doc(reference_texts.get("implementation-plan.md", ""), errors)

    validate_implementation_layout_doc(reference_texts.get("implementation-layout.md", ""), errors)

    validate_observability_testing_doc(reference_texts.get("observability-testing.md", ""), errors)

    validate_response_contract_doc(reference_texts.get("response-contract.md", ""), errors)

    if errors:
        print("netty-handler-dispatcher 技能检查失败：")
        for error in errors:
            print(f"- {error}")
        return 1

    print("netty-handler-dispatcher 技能检查通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
