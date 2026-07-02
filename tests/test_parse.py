"""Tests for the parser: tokenizing, comments, whitespace, and encoding."""

from __future__ import annotations

import pytest

from markinp.model import DataType
from markinp.parse import parse_file, parse_text

from .conftest import FIXTURES, VALID_FILES


def test_basic_record_fields() -> None:
    result = parse_text("1001 1 0 10.5;\n")
    assert len(result.dataset.records) == 1
    record = result.dataset.records[0]
    assert record.history == "1001"
    assert record.raw_values == ["1", "0", "10.5"]
    assert record.line == 1


def test_leading_comment_attaches_to_record() -> None:
    result = parse_text("/* ind 001 */ 1001 1;\n")
    assert result.dataset.records[0].comment == "ind 001"


def test_trailing_comment_attaches_to_record() -> None:
    result = parse_text("1001 1; /* recaptured */\n")
    assert result.dataset.records[0].comment == "recaptured"


def test_comment_only_line_labels_next_record() -> None:
    result = parse_text("/* ind 001 */\n1001 1;\n")
    assert result.dataset.records[0].comment == "ind 001"


def test_crlf_line_endings_are_normalized() -> None:
    result = parse_text("101 1;\r\n110 2;\r\n")
    assert [r.history for r in result.dataset.records] == ["101", "110"]
    assert [r.line for r in result.dataset.records] == [1, 2]


def test_blank_lines_are_skipped_but_line_numbers_kept() -> None:
    result = parse_text("101 1;\n\n\n110 2;\n")
    assert [r.line for r in result.dataset.records] == [1, 4]


def test_bom_is_stripped_and_flagged() -> None:
    result = parse_file(FIXTURES / "bom.inp")
    assert {d.code for d in result.diagnostics} >= {"MK020"}
    assert result.dataset.records[0].history == "101"


def test_infers_single_group_no_covariates() -> None:
    result = parse_file(FIXTURES / "valid_single_group.inp")
    assert result.dataset.n_occasions == 3
    assert result.dataset.n_groups == 1
    assert result.dataset.n_covariates == 0
    assert result.dataset.data_type == DataType.LIVE_RECAPTURE


def test_infers_covariate_column_from_decimal() -> None:
    result = parse_file(FIXTURES / "valid_covariates.inp")
    assert result.dataset.n_groups == 1
    assert result.dataset.n_covariates == 1


def test_infers_multistrata_from_letters() -> None:
    result = parse_file(FIXTURES / "multistrata.inp")
    assert result.dataset.data_type == DataType.MULTISTRATA


@pytest.mark.parametrize("name", VALID_FILES)
def test_valid_fixtures_parse_without_parse_errors(name: str) -> None:
    result = parse_file(FIXTURES / name)
    assert all(d.code != "MK001" for d in result.diagnostics)
    assert result.dataset.records
