"""Tests for the validator: every diagnostic code has a triggering fixture."""

from __future__ import annotations

import pytest

from markinp.model import DataType, Severity
from markinp.parse import parse_file
from markinp.validate import validate

from .conftest import FIXTURES, VALID_FILES


def codes_for(name: str, **kwargs: object) -> set[str]:
    """Parse a fixture and return the set of diagnostic codes it produces."""
    result = parse_file(FIXTURES / name)
    diagnostics = result.diagnostics + validate(result.dataset, **kwargs)  # type: ignore[arg-type]
    return {d.code for d in diagnostics}


# --- one fixture per code -------------------------------------------------


def test_mk001_missing_semicolon() -> None:
    assert "MK001" in codes_for("missing_semicolon.inp")


def test_mk002_ragged_history() -> None:
    assert "MK002" in codes_for("ragged_history.inp")


def test_mk003_nonnumeric_frequency() -> None:
    assert "MK003" in codes_for("nonnumeric_frequency.inp")


def test_mk004_frequency_count() -> None:
    assert "MK004" in codes_for("frequency_count.inp")


def test_mk005_illegal_history_char() -> None:
    # A non-0/1 character is only an "illegal character" once the file is
    # asserted to be standard; by default a non-standard alphabet is MK900.
    assert "MK005" in codes_for("illegal_history_char.inp", data_type=DataType.LIVE_RECAPTURE)


def test_mk006_covariate_count() -> None:
    assert "MK006" in codes_for("covariate_count.inp")


def test_mk007_missing_covariate() -> None:
    assert "MK007" in codes_for("missing_covariate.inp")


def test_mk008_no_records() -> None:
    assert "MK008" in codes_for("empty_file.inp")


def test_mk009_unterminated_comment() -> None:
    assert "MK009" in codes_for("unterminated_comment.inp")


def test_mk010_wrong_asserted_occasions() -> None:
    assert "MK010" in codes_for("valid_single_group.inp", occasions=4)


def test_mk011_all_zero_history() -> None:
    assert "MK011" in codes_for("all_zero_history.inp")


def test_mk012_negative_frequency() -> None:
    assert "MK012" in codes_for("negative_frequency.inp")


def test_mk013_uncollapsed_duplicates() -> None:
    assert "MK013" in codes_for("duplicates.inp")


def test_mk014_noninteger_frequency() -> None:
    assert "MK014" in codes_for("noninteger_frequency.inp")


def test_mk015_content_after_semicolon() -> None:
    assert "MK015" in codes_for("content_after_semicolon.inp")


def test_mk016_mixed_whitespace() -> None:
    assert "MK016" in codes_for("mixed_whitespace.inp")


def test_mk017_illegal_stratum() -> None:
    assert "MK017" in codes_for("illegal_stratum.inp")


def test_mk018_odd_ldld_columns() -> None:
    codes = codes_for("valid_single_group.inp", data_type=DataType.KNOWN_FATE)
    assert "MK018" in codes


def test_mk019_empty_group() -> None:
    assert "MK019" in codes_for("empty_group.inp")


def test_mk020_encoding_bom() -> None:
    assert "MK020" in codes_for("bom.inp")


def test_mk900_partial_support_multistrata() -> None:
    assert "MK900" in codes_for("multistrata.inp")


def test_mk900_nonstandard_alphabet_by_default() -> None:
    # A file with an unsupported alphabet (here '2', a certain-detection code) is
    # detected as non-standard and reported once as MK900 rather than a flood of
    # MK005 illegal-character errors.
    codes = codes_for("nonstandard_alphabet.inp")
    assert "MK900" in codes
    assert "MK005" not in codes


def test_nonstandard_alphabet_is_strict_when_asserted_standard() -> None:
    codes = codes_for("nonstandard_alphabet.inp", data_type=DataType.LIVE_RECAPTURE)
    assert "MK005" in codes


# --- occupancy (data type with '.' for a not-surveyed occasion) -----------


def test_occupancy_file_is_clean() -> None:
    # 0/1/'.' histories are first-class occupancy data: no MK900, no MK005, and
    # crucially no MK011 (an all-zero site is valid, informative occupancy data).
    codes = codes_for("occupancy.inp")
    assert codes == set()


def test_mk021_all_missing_history() -> None:
    codes = codes_for("occupancy_all_missing.inp")
    assert "MK021" in codes


def test_occupancy_flags_illegal_char_when_asserted() -> None:
    # Assert occupancy on a file whose alphabet is not 0/1/'.': the stray char
    # is reported as MK005.
    codes = codes_for("nonstandard_alphabet.inp", data_type=DataType.OCCUPANCY)
    assert "MK005" in codes


# --- clean files stay clean ----------------------------------------------


@pytest.mark.parametrize("name", VALID_FILES)
def test_valid_files_have_no_errors(name: str) -> None:
    result = parse_file(FIXTURES / name)
    diagnostics = result.diagnostics + validate(result.dataset)
    errors = [d for d in diagnostics if d.severity == Severity.ERROR]
    assert errors == []


@pytest.mark.parametrize("name", VALID_FILES)
def test_valid_files_have_no_diagnostics_at_all(name: str) -> None:
    result = parse_file(FIXTURES / name)
    diagnostics = result.diagnostics + validate(result.dataset)
    assert diagnostics == []


# --- assertion behaviour --------------------------------------------------


def test_asserted_groups_flags_mismatch() -> None:
    # valid_covariates has two value columns; asserting three groups makes every
    # record's frequency-column count wrong.
    codes = codes_for("valid_covariates.inp", groups=3, covariates=0)
    assert "MK004" in codes


def test_asserted_correct_structure_is_clean() -> None:
    codes = codes_for("valid_covariates.inp", groups=1, covariates=1, occasions=4)
    assert codes == set()


def test_diagnostics_are_sorted_by_line() -> None:
    result = parse_file(FIXTURES / "empty_group.inp")
    diagnostics = validate(result.dataset)
    lines = [d.line for d in diagnostics if d.line is not None]
    assert lines == sorted(lines)
