"""Signed session tokens (spec 0002, AC-4)."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from leave_manager.core.tokens import SessionToken, sign, verify

SECRET = "unit-test-secret"
TOKEN = SessionToken(user_id=7, issued_at=datetime(2026, 11, 7, 9, 0, tzinfo=UTC), csrf="abc123")


def test_signed_token_round_trips() -> None:
    assert verify(sign(TOKEN, SECRET), SECRET) == TOKEN


def test_tampered_token_is_rejected() -> None:
    raw = sign(TOKEN, SECRET)
    payload, _, signature = raw.partition(".")
    other_payload = sign(SessionToken(1, TOKEN.issued_at, TOKEN.csrf), SECRET).partition(".")[0]

    assert verify(f"{other_payload}.{signature}", SECRET) is None  # another user's payload
    assert verify(f"{payload}.{signature[:-1]}A", SECRET) is None  # altered signature
    assert verify(raw, "another-secret") is None


@pytest.mark.parametrize("raw", ["", ".", "abc", "abc.", ".abc", "ü.ü", "a.b.c", "!!!.???"])
def test_malformed_token_is_rejected(raw: str) -> None:
    assert verify(raw, SECRET) is None
