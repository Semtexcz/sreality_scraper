"""Shared pytest fixtures for deterministic scraper tests."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest


@dataclass
class FakeResponse:
    """Minimal HTTP response stub for parser unit tests."""

    text: str


@pytest.fixture
def response_factory() -> type[FakeResponse]:
    """Return a response class that mimics ``requests.Response`` text access."""

    return FakeResponse


@pytest.fixture
def html_fixture_dir() -> Path:
    """Return the directory containing representative HTML test fixtures."""

    return Path(__file__).parent / "fixtures"


@pytest.fixture
def html_fixture_loader(html_fixture_dir: Path):
    """Return a helper that loads representative HTML fixtures by filename."""

    def load_fixture(name: str) -> str:
        """Load one HTML fixture from the shared fixtures directory."""

        return (html_fixture_dir / name).read_text(encoding="utf-8")

    return load_fixture
