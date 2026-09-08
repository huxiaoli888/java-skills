from __future__ import annotations

from netty_skill_rules import canonicalization, replay, tcp_udp, websocket


def validate_protocol_signature_replay_doc(protocol_text: str, errors: list[str]) -> None:
    replay.validate_protocol_signature_replay_doc(protocol_text, errors)


def validate_tcp_udp_doc(tcp_udp_text: str, errors: list[str]) -> None:
    tcp_udp.validate_tcp_udp_doc(tcp_udp_text, errors)


def validate_signature_canonicalization_doc(signature_text: str, errors: list[str], replay_key_text: tuple[str, ...]) -> None:
    canonicalization.validate_signature_canonicalization_doc(signature_text, errors, replay_key_text)


def validate_signature_builder_boundaries_doc(signature_text: str, errors: list[str]) -> None:
    canonicalization.validate_signature_builder_boundaries_doc(signature_text, errors)


def validate_websocket_doc(websocket_text: str, errors: list[str], websocket_http_rest_boundary_text: tuple[str, ...]) -> None:
    websocket.validate_websocket_doc(websocket_text, errors, websocket_http_rest_boundary_text)
