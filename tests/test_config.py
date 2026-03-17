"""Tests for runtime configuration defaults and environment overrides."""

from __future__ import annotations

from scraperweb.config import Settings, get_settings


def test_get_settings_uses_defaults_when_environment_is_missing(monkeypatch) -> None:
    """Ensure default settings are used when env vars are not set."""

    monkeypatch.delenv("MONGODB_URI", raising=False)
    monkeypatch.delenv("MONGODB_DATABASE", raising=False)
    monkeypatch.delenv("GEOPY_USER_AGENT", raising=False)

    assert get_settings() == Settings(
        mongodb_uri="mongodb://localhost:27017",
        mongodb_database="RealEstates",
        geopy_user_agent="scraperweb",
    )


def test_get_settings_reads_environment_overrides(monkeypatch) -> None:
    """Ensure settings are loaded from environment variables when provided."""

    monkeypatch.setenv("MONGODB_URI", "mongodb://example.test:27017")
    monkeypatch.setenv("MONGODB_DATABASE", "TestDb")
    monkeypatch.setenv("GEOPY_USER_AGENT", "test-agent")

    assert get_settings() == Settings(
        mongodb_uri="mongodb://example.test:27017",
        mongodb_database="TestDb",
        geopy_user_agent="test-agent",
    )
