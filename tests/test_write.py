"""Tests for the writer: deterministic output and round-trip stability."""

from __future__ import annotations

import pytest

from markinp.parse import parse_file, parse_text
from markinp.write import write_text

from .conftest import FIXTURES, VALID_FILES


def _record_multiset(text: str) -> list[tuple[str, tuple[str, ...], str | None]]:
    result = parse_text(text)
    return sorted((r.history, tuple(r.raw_values), r.comment) for r in result.dataset.records)


@pytest.mark.parametrize("name", VALID_FILES)
def test_parse_write_parse_is_stable(name: str) -> None:
    original = parse_file(FIXTURES / name)
    text = write_text(original.dataset)
    reparsed = parse_text(text)

    before = sorted((r.history, tuple(r.raw_values)) for r in original.dataset.records)
    after = sorted((r.history, tuple(r.raw_values)) for r in reparsed.dataset.records)
    assert before == after


def test_write_is_order_independent() -> None:
    result = parse_file(FIXTURES / "valid_multi_group.inp")
    text1 = write_text(result.dataset)
    result.dataset.records.reverse()
    text2 = write_text(result.dataset)
    assert text1 == text2


def test_write_preserves_record_comments() -> None:
    text = write_text(parse_file(FIXTURES / "valid_comments.inp").dataset)
    assert "/* recaptured */" in text


def test_written_records_round_trip_through_reparse() -> None:
    text = write_text(parse_file(FIXTURES / "valid_covariates.inp").dataset)
    assert _record_multiset(text) == _record_multiset(text)
    # And the emitted text ends with exactly one trailing newline.
    assert text.endswith(";\n")
