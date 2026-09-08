from __future__ import annotations

import re


def _add_error(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_protocol_signature_replay_doc(protocol_text: str, errors: list[str]) -> None:
    if not protocol_text:
        return
    if "建议包含：HTTP method" in protocol_text:
        _add_error(errors, "protocol-format.md 不应把签名原文字段描述为建议包含，应使用签名原文必须包含固定字段槽位")
    for text in ["TCP/UDP 高风险或已识别设备请求必填，匿名公开探测可省略", "匿名公开探测可省略 `udid` 和签名材料"]:
        if text not in protocol_text:
            _add_error(errors, f"protocol-format.md 必须说明匿名公开探测与 udid 的边界：{text}")
    for text in ["高风险、签名或防重放请求必填；低风险请求建议", "请求侧用于重放窗口校验"]:
        if text not in protocol_text:
            _add_error(errors, f"protocol-format.md 的 ts 字段必须区分高风险必填与低风险建议：{text}")
    for text in ["需要防重放或幂等的范围内必须唯一", "HTTP/UDP 按 replay key 或业务幂等维度约束"]:
        if text not in protocol_text:
            _add_error(errors, f"protocol-format.md 必须说明 reqid/replay cache 边界：{text}")
    for text in ["传输响应摘要", "业务幂等结果必须由 service 层按业务键持久化或可靠存储", "不能放进 `ReplayCache`"]:
        if text not in protocol_text:
            _add_error(errors, f"protocol-format.md 必须区分 replay 响应摘要与业务幂等结果：{text}")
