"""Shared pytest fixtures and helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"

VALID_FILES = [
    "valid_single_group.inp",
    "valid_multi_group.inp",
    "valid_covariates.inp",
    "valid_comments.inp",
]


@pytest.fixture
def fixtures() -> Path:
    """Absolute path to the test fixtures directory."""
    return FIXTURES
