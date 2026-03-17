"""Shared pytest fixtures for deterministic scraper tests."""

from __future__ import annotations

from dataclasses import dataclass

import pytest


@dataclass
class FakeResponse:
    """Minimal HTTP response stub for parser unit tests."""

    text: str


@pytest.fixture
def response_factory() -> type[FakeResponse]:
    """Return a response class that mimics ``requests.Response`` text access."""

    return FakeResponse
