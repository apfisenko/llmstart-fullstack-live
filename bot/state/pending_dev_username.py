"""Ожидание ввода username после /login (память процесса; сбрасывается при рестарте)."""

from __future__ import annotations

_waiting: set[int] = set()


def mark_waiting_username(chat_id: int) -> None:
    _waiting.add(chat_id)


def is_waiting_username(chat_id: int) -> bool:
    return chat_id in _waiting


def clear_waiting_username(chat_id: int) -> None:
    _waiting.discard(chat_id)
