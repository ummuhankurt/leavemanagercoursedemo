"""Startup refuses without a session secret (spec 0002, AC-10)."""

from __future__ import annotations

import pytest

from leave_manager.core.config import COOKIE_SECURE_ENV, SESSION_SECRET_ENV, Settings
from leave_manager.core.errors import ConfigurationError
from leave_manager.main import create_app


@pytest.mark.parametrize("value", [None, "", "   "])
def test_missing_session_secret_refuses_to_start_without_leaking(
    monkeypatch: pytest.MonkeyPatch, value: str | None
) -> None:
    if value is None:
        monkeypatch.delenv(SESSION_SECRET_ENV, raising=False)
    else:
        monkeypatch.setenv(SESSION_SECRET_ENV, value)

    with pytest.raises(ConfigurationError) as excinfo:
        create_app()

    assert SESSION_SECRET_ENV in str(excinfo.value)


def test_settings_read_secret_and_secure_flag_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(SESSION_SECRET_ENV, "s3cret-value")
    monkeypatch.setenv(COOKIE_SECURE_ENV, "true")

    settings = Settings.from_env()

    assert settings.session_secret == "s3cret-value"
    assert settings.cookie_secure is True
