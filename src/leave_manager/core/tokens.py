"""Signed session tokens: HMAC-SHA256 over a small JSON payload (plan 0002, R-1).

Signed, not encrypted: the payload holds no secret except the CSRF token, which the client is
given anyway. Expiry is decided by the service layer with its Clock, not here.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class SessionToken:
    user_id: int
    issued_at: datetime
    csrf: str


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64decode(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def _signature(payload: str, secret: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), payload.encode("ascii"), hashlib.sha256).digest()
    return _b64encode(digest)


def sign(token: SessionToken, secret: str) -> str:
    body = {
        "uid": token.user_id,
        "iat": int(token.issued_at.timestamp()),
        "csrf": token.csrf,
    }
    payload = _b64encode(json.dumps(body, separators=(",", ":")).encode("utf-8"))
    return f"{payload}.{_signature(payload, secret)}"


def verify(raw: str, secret: str) -> SessionToken | None:
    """The token's content when its signature is valid; None for anything else."""
    payload, sep, signature = raw.partition(".")
    if not sep or not payload or not signature:
        return None
    if not (payload.isascii() and signature.isascii()):
        return None
    expected = _signature(payload, secret)
    if not hmac.compare_digest(expected, signature):
        return None
    try:
        body = json.loads(_b64decode(payload))
        user_id, issued_at, csrf = body["uid"], body["iat"], body["csrf"]
    except (binascii.Error, ValueError, KeyError, TypeError):
        return None
    if not (isinstance(user_id, int) and isinstance(issued_at, int) and isinstance(csrf, str)):
        return None
    return SessionToken(
        user_id=user_id, issued_at=datetime.fromtimestamp(issued_at, UTC), csrf=csrf
    )
