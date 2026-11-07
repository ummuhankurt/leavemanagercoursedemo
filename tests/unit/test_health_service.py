"""Spec 0001 AC-1, AC-2 — status rules, without a database."""

from __future__ import annotations

import pytest

from leave_manager.core.errors import DatabaseUnavailableError, ServiceUnavailableError
from leave_manager.services.health import HealthStatus, get_status


class FakeProbe:
    def __init__(self, *, reachable: bool) -> None:
        self.reachable = reachable
        self.pinged = False

    def ping(self) -> None:
        self.pinged = True
        if not self.reachable:
            raise DatabaseUnavailableError("unreachable")


def test_status_ok_when_database_reachable() -> None:
    probe = FakeProbe(reachable=True)

    status = get_status(probe, version="1.2.3")

    assert probe.pinged
    assert status == HealthStatus(status="ok", version="1.2.3", database="reachable")


def test_status_unavailable_when_database_unreachable() -> None:
    with pytest.raises(ServiceUnavailableError) as raised:
        get_status(FakeProbe(reachable=False), version="1.2.3")

    assert raised.value.status_code == 503
    assert raised.value.code == "SERVICE_UNAVAILABLE"
    assert raised.value.message == "Hizmet şu anda kullanılamıyor."
